from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()
security = (
    HTTPBasic()
)  # 보안 유틸리티- 요청에서 인증헤드 추출, 이름과 비번을 HTTPBasicCredentials 객체로 파싱.


# 주입용 함수
# HTTPBasicCredentials 객체는 기본 인증 헤더에서 사용자 이름과 비밀번호를 추출한 결과
def verify_credit(credit: HTTPBasicCredentials = Depends(security)):
    ok_username = secrets.compare_digest(credit.username, "tomato")
    ok_password = secrets.compare_digest(credit.password, "1234")

    if not (ok_username and ok_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic realm=JWT"},
        )
    return credit.username


# 클라이언트 요청형태 - Base64로 인코딩한 name,password
# Authorization: Basic <base64_encoded_username:password>
# -> HTTPBasic()이 만든 security객체가 파싱해서 아이디, 패스워드 추출
# verify_credit가 검증하고 str형태로 돌려줌


@app.get("/secure-endpoint")
def secure_endpoint(username: str = Depends(verify_credit)):
    return {"welcome message": f"Hello,{username}"}
