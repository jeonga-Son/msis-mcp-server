import yaml
import requests
from fastmcp import FastMCP
import logging
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP 서버 생성
mcp = FastMCP("Demo")

# Swagger 불러오기
def load_openapi_from_url(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 핸들러 생성
def model_executor(input_data, model_name):
    logger.info(f"Tool 실행됨 - input_data: {input_data}, model_name: {model_name}")
    result = {"result": f"{model_name} handled {input_data}"}
    logger.info(f"Tool 실행 결과: {result}")
    return result

# OpenAPI spec 기반 핸들러 생성
def generate_mcp_handlers(openapi_spec):
    paths = openapi_spec.get("paths", {})
    logger.info(f"OpenAPI 스펙에서 {len(paths)}개의 경로를 찾았습니다.")
    
    for path, methods in paths.items():
        for method, config in methods.items():
            # 각 경로에 대해 기본 모델 이름 및 tool 이름 생성
            model_name = f"model_{path.replace('/', '_')}"
            tool_name = f"{method.lower()}_{path.replace('/', '_')}"
            
            logger.info(f"Tool 등록 중: {tool_name}")
            logger.info(f"  - 경로: {path}")
            logger.info(f"  - 메서드: {method.upper()}")
            logger.info(f"  - 모델: {model_name}")
            
            mcp.add_tool(
                fn=lambda input_data, model_name=model_name: model_executor(input_data, model_name),
                name=tool_name,
                description=f"Auto-generated tool for {path} [{method.upper()}]"
            )
            logger.info(f"Tool 등록 완료: {tool_name}")

# 루트 엔드포인트 핸들러
async def root(request):
    return JSONResponse({
        "message": "MCP Server is running",
        "endpoints": {
            "mcp": "/mcp",
            "tools": "/mcp/tools",
            "swagger": "https://petstore.swagger.io/v2/swagger.json"
        }
    })

# 실행
if __name__ == "__main__":
    logger.info("Starting MCP server...")
    swagger_url = "https://petstore.swagger.io/v2/swagger.json"
    openapi_spec = load_openapi_from_url(swagger_url)
    logger.info(f"Loaded OpenAPI spec from {swagger_url}")
    generate_mcp_handlers(openapi_spec)
    logger.info("All tools registered. Server is ready!")
    
    # HTTP 서버로 실행
    app = mcp.streamable_http_app()
    
    # 루트 엔드포인트 추가
    app.routes.insert(0, Route("/", root))
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
