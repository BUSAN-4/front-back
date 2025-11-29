from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from app.database import get_db

router = APIRouter()


@router.get("", response_model=None)
async def get_test_data(
    db: Session = Depends(get_db)
):
    """test 테이블의 모든 데이터 조회"""
    try:
        # test 테이블의 모든 데이터 가져오기
        result = db.execute(text("SELECT * FROM test"))
        rows = result.fetchall()
        
        # 컬럼 이름 가져오기
        columns = result.keys()
        
        # 딕셔너리 형태로 변환
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # datetime 등은 문자열로 변환
                if hasattr(value, 'isoformat'):
                    row_dict[col] = value.isoformat()
                else:
                    row_dict[col] = value
            data.append(row_dict)
        
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch test data: {str(e)}"
        )


@router.get("/count")
async def get_test_count(
    db: Session = Depends(get_db)
):
    """test 테이블의 레코드 수 조회"""
    try:
        result = db.execute(text("SELECT COUNT(*) as count FROM test"))
        count = result.fetchone()[0]
        return {"count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get count: {str(e)}"
        )