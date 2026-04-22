import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

app = FastAPI()

# 0. CORS 설정 추가 (브라우저 접근 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DB_DIR = os.path.join(BASE_DIR, "../db/chroma_mitre")

# 2. 임베딩 모델 로드 (GPU 가속 사용)
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={'device': 'cuda'},
    encode_kwargs={'normalize_embeddings': True}
)

# 3. 기존 벡터 DB 연결
if not os.path.exists(CHROMA_DB_DIR):
    print(f"[!] 경고: {CHROMA_DB_DIR} 경로에 벡터 DB가 없습니다. 먼저 embedder.py를 실행하세요.")

vector_db = Chroma(
    persist_directory=CHROMA_DB_DIR, 
    embedding_function=embeddings
)

# 4. LLM 설정 (Llama 3.2 3B)
llm = ChatOllama(
    model="llama3.2:3b", 
    temperature=0,
    num_gpu=1, 
    num_ctx=4096
)

# 5. 핵심 프롬프트 최적화
template = """### [보안 분석가 페르소나]
당신은 ISMS-P 및 OWASP 기준에 정통한 20년 경력의 수석 모의해킹 전문가입니다.
반드시 제공된 [지식베이스]의 내용을 바탕으로 사용자의 질문에 답하십시오.

### [지식베이스 (MITRE ATT&CK)]
{context}

### [지시사항]
1. 리포트의 모든 섹션은 반드시 한국어로 작성하십시오.
2. **절대로 [기법 ID]와 같은 대괄호 문구를 그대로 출력하지 마십시오.**
3. 지식베이스에 있는 실제 데이터(ID, 명칭, 원리)를 찾아 그 내용을 채워 넣으십시오.
4. 만약 지식베이스에 내용이 부족하다면, 당신의 전문 지식을 활용해 '실제로 동작 가능한' 수준으로 보충하십시오.

---
# [대상 OS] - [기법 ID]: [기법 명칭]

## 1. 공격 메커니즘 분석
* **MITRE 기법:** [실제 기법 이름 및 ID]
* **위험도:** [상/중/하] (ISMS-P 기준)

[공격의 동작 원리를 4단계로 나누어 기술하십시오.]

## 2. 실전 모의해킹 소스코드 (PoC)
```python
# 실제 동작 가능한 파이썬 소스코드를 작성하고 한국어 주석을 다십시오.
```

## 3. 입체적 대응 및 방어 전략
① 기술적 차단 및 패치 관리
[구체적인 방어 조치 및 설정값]

② 관리적 보안 강화
[인증 강화 또는 권한 제어 방안]

4. 관련 기술 참조 (External Links)
[지식베이스에서 찾은 MITRE 관련 URL]

5. ※주의
위 리포트는 교육 및 진단용입니다. 실제 공격 사용 시 법적 책임은 사용자에게 있습니다.
"""

prompt = PromptTemplate(template=template, input_variables=["context", "question"])

# 6. RAG 체인 조립
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_db.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={"prompt": prompt}
)

class Query(BaseModel):
    text: str

@app.post("/consult")
async def consult(query: Query):
    try:
        # RAG 엔진 실행
        response = await qa_chain.ainvoke(query.text)
        return {"result": response["result"]}
    except Exception as e:
        print(f"[!] Error: {str(e)}")
        raise HTTPException(status_code=500, detail="내부 서버 처리 중 오류가 발생했습니다.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)