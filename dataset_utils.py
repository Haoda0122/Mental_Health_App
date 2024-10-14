import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sentence_transformers import SentenceTransformer
import faiss
import pickle

def load_dataset(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or XLSX file.")

def get_dataset_info(df):
    info = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "column_types": df.dtypes.to_dict(),
        "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
        "date_columns": df.select_dtypes(include=['datetime64']).columns.tolist(),
    }
    
    for col in info["numeric_columns"]:
        info[f"{col}_stats"] = {
            "mean": df[col].mean(),
            "median": df[col].median(),
            "std": df[col].std(),
            "min": df[col].min(),
            "max": df[col].max()
        }
    
    return info

def search_dataset(df, query, column):
    if df[column].dtype == 'object':
        return df[df[column].str.contains(query, case=False, na=False)]
    elif np.issubdtype(df[column].dtype, np.number):
        try:
            value = float(query)
            return df[df[column] == value]
        except ValueError:
            return df.head(0)
    elif np.issubdtype(df[column].dtype, np.datetime64):
        try:
            date = pd.to_datetime(query)
            return df[df[column] == date]
        except ValueError:
            return df.head(0)
    else:
        return df.head(0)

def generate_charts(df):
    charts = []
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_columns = df.select_dtypes(include=['object']).columns

    if len(numeric_columns) == 0 and len(categorical_columns) == 0:
        return [plt.figure(figsize=(8, 6))]

    if len(categorical_columns) > 0:
        for col in categorical_columns[:2]:
            fig, ax = plt.subplots()
            df[col].value_counts().plot(kind='bar', ax=ax)
            ax.set_title(f'Distribution of {col}')
            ax.set_ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            charts.append(fig)

            fig, ax = plt.subplots()
            df[col].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_title(f'Distribution of {col}')
            plt.axis('equal')
            plt.tight_layout()
            charts.append(fig)

    for col in numeric_columns:
        fig, ax = plt.subplots()
        sns.histplot(df[col], kde=True, ax=ax)
        ax.set_title(f'Distribution of {col}')
        ax.set_xlabel(col)
        ax.set_ylabel('Count')
        plt.tight_layout()
        charts.append(fig)

    date_columns = df.select_dtypes(include=['datetime64']).columns
    if len(date_columns) > 0 and len(numeric_columns) > 0:
        date_col = date_columns[0]
        fig, ax = plt.subplots()
        df.plot(x=date_col, y=numeric_columns[0], ax=ax)
        ax.set_title(f'{numeric_columns[0]} over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel(numeric_columns[0])
        plt.tight_layout()
        charts.append(fig)

    return charts

def generate_embeddings(texts):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode(texts)

def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    return index

def save_faiss_index(index, file_path):
    faiss.write_index(index, file_path)

def load_faiss_index(file_path):
    return faiss.read_index(file_path)

def store_dataset_embeddings(df, text_column, index_file_path, metadata_file_path):
    texts = df[text_column].tolist()
    embeddings = generate_embeddings(texts)
    index = create_faiss_index(embeddings)
    save_faiss_index(index, index_file_path)
    
    metadata = {
        'text_column': text_column,
        'index_file_path': index_file_path,
        'original_data': df.to_dict(orient='records')
    }
    with open(metadata_file_path, 'wb') as f:
        pickle.dump(metadata, f)

def load_dataset_embeddings(index_file_path, metadata_file_path):
    index = load_faiss_index(index_file_path)
    with open(metadata_file_path, 'rb') as f:
        metadata = pickle.load(f)
    return index, metadata

def search_similar_texts(query, index, metadata, k=5):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([query])
    D, I = index.search(query_embedding.astype('float32'), k)
    results = [metadata['original_data'][i] for i in I[0]]
    return results