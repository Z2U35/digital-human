
import json
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import torch
import dashscope
import random
import time
from http import HTTPStatus
import re

dashscope.api_key = "sk-282326c395714aba8c4c051955eb22a2"

# 读取数据
file_path = r'jmu_data/output.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

df = pd.DataFrame(data)

# 加载预训练模型
tokenizer = AutoTokenizer.from_pretrained('uer/sbert-base-chinese-nli')
model = AutoModel.from_pretrained('uer/sbert-base-chinese-nli')

def clean_content(content):
    """清理内容中的HTML标签和URL"""
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'http\S+', '', content)
    return content

def encode_content(row):
    """对内容进行编码"""
    title = row['title']
    content = clean_content(row['content'])[:20]
    title_inputs = tokenizer(title, return_tensors='pt', max_length=512, truncation=True, padding='max_length')
    with torch.no_grad():
        title_outputs = model(**title_inputs)
    title_vector = title_outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    content_inputs = tokenizer(content, return_tensors='pt', max_length=512, truncation=True, padding='max_length')
    with torch.no_grad():
        content_outputs = model(**content_inputs)
    content_vector = content_outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    combined_vector = 0.55 * title_vector + 0.45 * content_vector
    return combined_vector

df['encoded'] = df.apply(encode_content, axis=1)
categories = df['title'].unique()
category_vectors = {category: np.array(df[df['title'] == category]['encoded'].tolist()) for category in categories}

def classify_and_retrieve(question):
    """分类并检索相关内容"""
    inputs = tokenizer(question, return_tensors='pt', max_length=512, truncation=True, padding='max_length')
    with torch.no_grad():
        question_vector = model(**inputs).last_hidden_state.mean(dim=1).squeeze().numpy()
    scores_dict = {}
    for category, vectors in category_vectors.items():
        scores = cosine_similarity([question_vector], vectors)[0]
        max_score = np.max(scores)
        scores_dict[category] = max_score
    sorted_scores = sorted(scores_dict.items(), key=lambda item: item[1], reverse=True)[:3]
    best_articles = []
    for category, score in sorted_scores:
        if score > 0.5:
            best_article_idx = np.argmax(cosine_similarity([question_vector], category_vectors[category])[0])
            best_article = df[(df['title'] == category)].iloc[best_article_idx]
            best_articles.append(best_article['content'])
    return best_articles if best_articles else None

def call_with_messages(question, background_list=None):
    """调用API获取答案"""
    if background_list:
        background_content = "\n\n".join(background_list)
        messages = [{'role': 'user', 'content': f'{question}，请你根据以下背景知识以及结合你的资料回答我的问题,若背景知识不包含相关内容，则调用你自己的资料库,建议你的回答在100字以内：\n\n{background_content}'}]
    else:
        messages = [{'role': 'user', 'content': question}]
    seed = random.randint(1, 10000)
    start_time = time.time()
    response = dashscope.Generation.call(
        'qwen2-72b-instruct',
        messages=messages,
        seed=seed,
        result_format='message',
    )
    end_time = time.time()
    response_time = end_time - start_time
    if response.status_code == HTTPStatus.OK:
        content = response.output['choices'][0]['message']['content']
        return content
    else:
        return None

def get_response_from_llm(question):
    """获取LLM的响应"""
    background = classify_and_retrieve(question)
    response = call_with_messages(question, background)
    return response
