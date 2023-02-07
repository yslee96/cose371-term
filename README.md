# DB WEB Application

웹과 데이터베이스를 연동하여 등록된 사용자들이 물건을 거래할 수 있는 사이트를 제작한다. 

## 요구 및 구현 사항
- 중고 거래 사이트에 필요한 ER 디자인 및 DB 스키마 설계
- 로그인, 회원가입 + 중복 여부에 따른 성공,실패 처리
- ‘admin’의 id로 로그인했을 때만 사용할 수 있는 기능 (유저정보, 거래정보)
- 거래 사이트의 현재 정보 (거래 횟수가 가장 많은 상품 category, 구매/판매 비용이 가장 많은 사용자의 id)
- 사용자들은 거래를 위해 물건을 추가하거나 구매할 수 있음, 만약 (code, name, price, seller)가 일치하는 물건이 있다면 기존 물건의 stock에 더함
- 구매가 진행되는 경우 구매자의 rating에 따라 할인이 됨. 구매자는 할인된 금액만큼 balance에서 차감, 판매자는 할인 전 금액만큼 balance에 가산.
- 변경된 balance에 맞게 rating_info 테이블에서 condition을 확인하고 구매자와 판매자의 rating을 업데이트

## 데이터 베이스 스키마
<img width="992" alt="image" src="https://user-images.githubusercontent.com/77106988/217192948-ed70c6d5-709f-473c-8247-ca3b82459020.png">

## Result
- 로그인 , 회원가입
<img width="549" alt="image" src="https://user-images.githubusercontent.com/77106988/217204113-edf881e6-0415-4596-b08d-5e30792ec898.png">
<img width="337" alt="image" src="https://user-images.githubusercontent.com/77106988/217203883-0a13013b-b847-44f0-8c01-006f6d20abe4.png">

- Admin 기능
<img width="301" alt="image" src="https://user-images.githubusercontent.com/77106988/217203722-b094d63e-8770-4935-95ca-2427febef70c.png">
<img width="637" alt="image" src="https://user-images.githubusercontent.com/77106988/217203654-47795371-ea2e-4dba-bbbe-c8e89dcea9bc.png">
<img width="450" alt="image" src="https://user-images.githubusercontent.com/77106988/217204629-0db670eb-26c1-4ba3-8bd7-7e56aacdb366.png">

- 기타
<img width="297" alt="image" src="https://user-images.githubusercontent.com/77106988/217204362-ddcf7beb-e33b-406f-8ae1-9684a2a708d2.png">
<img width="247" alt="image" src="https://user-images.githubusercontent.com/77106988/217204460-5c7619ca-ecde-41e2-b4ba-67f35ca937ca.png">
<img width="404" alt="image" src="https://user-images.githubusercontent.com/77106988/217204549-7a99da91-afc6-42f1-af56-86c0dca20a1b.png">


