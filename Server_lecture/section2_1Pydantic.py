from pydantic import BaseModel, validator, field_validator

#1. 모델 생성 및  json변환 - 생성시에도 자동으로 유효성검사

class Item(BaseModel):
    name: str   # 타입힌트로 정의 # 필수필드
    description: str = None # 선택적 필드
    price: float
    tax: float = 0.0

item = Item(name="Apple",description = "Red fruit",  price=5.5)

#모델을 활용 파이썬 인스턴스를 만들고,  인스턴스를 json으로, json을 파이썬 인스턴스(객체) 변환할 수 있다.

#JSON 직렬화 인스턴스 모델을 json으로 변환
item_json = item.model_dump_json()
print("JSON:", item_json)

# JSON 역질렬환 json을 다시 파이썬 모델 인스턴스로 변환
item_obj = Item.model_validate_json(item_json)
print("OBject:",item_obj)

#2. validator 사용 조건부 유효성 검사

class User(BaseModel):
    name: str
    age: int

    @field_validator("age")
    def check_age(cls, v): # cls는 클래스 자체를 의미 self와 같은 역할 value = age
        if v <18:
            raise ValueError("No Teenager")
        return v

#3. 복잡한 타입과 중첩된 모델 사용하기

from typing import List

class Item_simple(BaseModel):
    name: str
    price: float

#모델안에서 모델 사용
class Order(BaseModel):
    id: int
    items: List[Item_simple]

order = Order(id=123, items=[{"name":"Apple", "price":5.5}, {"name":"Banana", "price":2.5}])


order_json = order.model_dump_json()
print("JSON:",order_json)
order_model = Order.model_validate_json(order_json)
print("OBject:",order_model)

#4. ORM 모드
# Pydantic은 ORM 모드를 지원한다. ORM 모드는 데이터베이스에서 데이터를 가져와 Pydantic 모델로 쉽게 변환할 수 있다.

class ORMModel: #예시 ORM 모델
    def __init__(self, name, age):
        self.name = name
        self.age = age

class UserModel(BaseModel):
    name: str
    age: int

# 이설정을 안하면 ORM에서 모델을 데이터 변환할수가 없으므로 에러가 남
    class Config:
        from_attributes= True # ORM 모델에서 데이터를 가져올 수 있도록 설정 orm_mode = True 대신


orm_user = ORMModel(name="Alice", age=25)
print("ORM:",orm_user)
# ORM 모델을 Pydantic 모델로 변환
user = UserModel.model_validate(orm_user)
print("Pydentic object:",user)