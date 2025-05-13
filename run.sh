python -m venv venv

# 가상환경 활성화
source ./venv/bin/activate

# Python 파일 실행
python mcp-server.py

# Test
python mcp-server.py --file example-openapi.json
python mcp-server.py --url https://petstore.swagger.io/v2/swagger.json