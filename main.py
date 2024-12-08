from fastapi import FastAPI, Query, HTTPException


from models import AddTextModel
from models import ProcessedTextModel, SearchResultModel
from text_operator import PipelineNLP, TextWriter, TextSearcher

# Инициализация
pipeline_nlp = PipelineNLP()
text_searcher = TextSearcher()
app = FastAPI()



# API для обработки текста
@app.post("/process")
def process_text(input_text: str) -> ProcessedTextModel:
    processed = pipeline_nlp.preprocess_text(input_text)
    return ProcessedTextModel(**{"processed_text": processed})


# API для поиска
@app.get("/search")
def search(
    query: str = Query(..., description="Текстовый запрос"),
) -> SearchResultModel:
    results = text_searcher.find_top_n(query)
    return SearchResultModel(**{"query": query, "results": results})


@app.post("/add_text")
def add_text(text: str) -> AddTextModel:
    res = TextWriter.add(text)
    if res:
        return res
    else:
        raise HTTPException(status_code=404, detail="not found")


# Запуск сервера
# uvicorn main:app --reload
