from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional
from datetime import datetime
from app.database import get_db, get_busan_car_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.busan_car_models import (
    BusanCarDrivingSession as DrivingSession,
    BusanCarDrivingSessionInfo as DrivingSessionInfo,
    BusanCarDrowsyDrive as DrowsyDrive,
    BusanCarUserVehicle as UserVehicle
)

router = APIRouter()


@router.get("", response_model=List[dict])
async def get_trips(
    car_id: Optional[str] = Query(None, description="차량 ID로 필터링"),
    session_id: Optional[str] = Query(None, description="세션 ID로 필터링"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_busan_car_db)
):
    """주행 세션 목록 조회 (driving_session 테이블)"""
    query = db.query(DrivingSession)
    
    if car_id:
        query = query.filter(DrivingSession.car_id == car_id)
    
    if session_id:
        query = query.filter(DrivingSession.session_id == session_id)
    
    if start_date:
        query = query.filter(DrivingSession.start_time >= start_date)
    
    if end_date:
        query = query.filter(DrivingSession.start_time <= end_date)
    
    sessions = query.order_by(DrivingSession.start_time.desc()).all()
    
    return [{
        "sessionId": s.session_id,
        "carId": s.car_id,
        "startTime": s.start_time.isoformat() if s.start_time else None,
        "endTime": s.end_time.isoformat() if s.end_time else None,
        "createdAt": s.created_at.isoformat() if s.created_at else None,
        "updatedAt": s.updated_at.isoformat() if s.updated_at else None
    } for s in sessions]


@router.get("/{session_id}", response_model=dict)
async def get_trip(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_busan_car_db)
):
    """주행 세션 상세 조회"""
    session = db.query(DrivingSession).filter(
        DrivingSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    
    return {
        "sessionId": session.session_id,
        "carId": session.car_id,
        "startTime": session.start_time.isoformat() if session.start_time else None,
        "endTime": session.end_time.isoformat() if session.end_time else None,
        "createdAt": session.created_at.isoformat() if session.created_at else None,
        "updatedAt": session.updated_at.isoformat() if session.updated_at else None
    }


@router.get("/{session_id}/info", response_model=List[dict])
async def get_trip_info(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_busan_car_db)
):
    """주행 세션 상세 정보 조회 (driving_session_info 테이블)"""
    # 세션 존재 확인
    session = db.query(DrivingSession).filter(
        DrivingSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    
    # 세션 정보 조회
    infos = db.query(DrivingSessionInfo).filter(
        DrivingSessionInfo.session_id == session_id
    ).order_by(DrivingSessionInfo.dt).all()
    
    return [{
        "infoId": i.info_id,
        "sessionId": i.session_id,
        "appLat": i.app_lat,
        "appLon": i.app_lon,
        "appPrevLat": i.app_prev_lat,
        "appPrevLon": i.app_prev_lon,
        "voltage": i.voltage,
        "dDoor": i.d_door,
        "pDoor": i.p_door,
        "rdDoor": i.rd_door,
        "rpDoor": i.rp_door,
        "tDoor": i.t_door,
        "engineStatus": i.engine_status,
        "rEngineStatus": i.r_engine_status,
        "sttAlert": i.stt_alert,
        "elStatus": i.el_status,
        "detectShock": i.detect_shock,
        "remainRemote": i.remain_remote,
        "autodoorUse": i.autodoor_use,
        "silenceMode": i.silence_mode,
        "lowVoltageAlert": i.low_voltage_alert,
        "lowVoltageEngine": i.low_voltage_engine,
        "temperature": i.temperature,
        "appTravel": i.app_travel,
        "appAvgSpeed": i.app_avg_speed,
        "appAccel": i.app_accel,
        "appGradient": i.app_gradient,
        "appRapidAcc": i.app_rapid_acc,
        "appRapidDeacc": i.app_rapid_deacc,
        "speed": i.speed,
        "createdDate": i.createdDate.isoformat() if i.createdDate else None,
        "appWeatherStatus": i.app_weather_status,
        "appPrecipitation": i.app_precipitation,
        "dt": i.dt.isoformat() if i.dt else None,
        "roadname": i.roadname,
        "treveltime": i.treveltime,
        "hour": i.Hour
    } for i in infos]


@router.get("/best-drivers/monthly", response_model=List[dict])
async def get_best_drivers_monthly(
    year: int = Query(..., description="연도 (예: 2024)"),
    month: int = Query(..., description="월 (1-12)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_busan_car_db)
):
    """
    월별 베스트 드라이버 Top 10 조회
    
    점수 계산 기준:
    - 급가속 (app_rapid_acc) - 낮을수록 좋음
    - 급감속 (app_rapid_deacc) - 낮을수록 좋음
    - 눈 감음 횟수 (gaze_closure) - 낮을수록 좋음
    
    점수 = 1000 - (급가속 합계 + 급감속 합계 + 눈감음 합계) * 가중치
    """
    # 월별 베스트 드라이버를 계산하는 SQL 쿼리 (createdDate 기준)
    query = text("""
        SELECT 
            ds.car_id,
            uv.user_car_brand,
            uv.user_car_model,
            uv.age,
            uv.user_sex,
            uv.user_location,
            COALESCE(SUM(COALESCE(dsi.app_rapid_acc, 0)), 0) as total_rapid_acc,
            COALESCE(SUM(COALESCE(dsi.app_rapid_deacc, 0)), 0) as total_rapid_deacc,
            COALESCE(SUM(COALESCE(dd.gaze_closure, 0)), 0) as total_gaze_closure,
            COUNT(DISTINCT ds.session_id) as session_count
        FROM driving_session ds
        LEFT JOIN uservehicle uv ON ds.car_id = uv.car_id
        LEFT JOIN driving_session_info dsi ON ds.session_id = dsi.session_id
        LEFT JOIN drowsy_drive dd ON ds.session_id = dd.session_id
        WHERE YEAR(dsi.createdDate) = :year
          AND MONTH(dsi.createdDate) = :month
          AND dsi.createdDate IS NOT NULL
        GROUP BY ds.car_id, uv.user_car_brand, uv.user_car_model, uv.age, uv.user_sex, uv.user_location
        HAVING COUNT(DISTINCT ds.session_id) > 0
        ORDER BY (
            (COALESCE(SUM(COALESCE(dsi.app_rapid_acc, 0)), 0) + 
             COALESCE(SUM(COALESCE(dsi.app_rapid_deacc, 0)), 0) + 
             COALESCE(SUM(COALESCE(dd.gaze_closure, 0)), 0)) / 
            NULLIF(COUNT(DISTINCT ds.session_id), 0)
        ) ASC
        LIMIT 10
    """)
    
    result = db.execute(query, {"year": year, "month": month})
    rows = result.fetchall()
    
    best_drivers = []
    for idx, row in enumerate(rows, 1):
        total_rapid_acc = row[6] or 0
        total_rapid_deacc = row[7] or 0
        total_gaze_closure = row[8] or 0
        session_count = row[9] or 1  # 0으로 나누기 방지
        
        # 총 사고 횟수
        total_incidents = total_rapid_acc + total_rapid_deacc + total_gaze_closure
        
        # 발생률 계산 (세션당 평균 사고 횟수)
        # 세션 수가 많을수록 더 공정한 평가를 위해 발생률 사용
        if session_count > 0:
            incident_rate = total_incidents / session_count
        else:
            incident_rate = 0
        
        # 점수 계산: 발생률 기반 (낮을수록 좋음)
        # 발생률 0.0 = 1000점, 발생률 1.0 = 0점
        # 발생률이 0.1 (세션당 0.1회) = 900점
        driver_score = max(0, 1000 - (incident_rate * 1000))
        
        best_drivers.append({
            "rank": idx,
            "carId": row[0],
            "carBrand": row[1],
            "carModel": row[2],
            "driverAge": row[3],
            "driverSex": row[4],
            "driverLocation": row[5],
            "totalRapidAcc": int(total_rapid_acc),
            "totalRapidDeacc": int(total_rapid_deacc),
            "totalGazeClosure": int(total_gaze_closure),
            "totalScore": int(total_incidents),
            "driverScore": round(driver_score, 2),
            "sessionCount": session_count,
            "incidentRate": round(incident_rate, 4)  # 발생률 추가
        })
    
    return best_drivers


@router.get("/best-drivers/monthly/list", response_model=List[dict])
async def get_best_drivers_monthly_list(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_busan_car_db)
):
    """
    월별 베스트 드라이버 목록 조회 (모든 월)
    각 월별로 Top 10을 반환
    """
    # 모든 월별 데이터를 가져오는 쿼리 (createdDate 기준)
    query = text("""
        SELECT 
            YEAR(dsi.createdDate) as year,
            MONTH(dsi.createdDate) as month,
            ds.car_id,
            uv.user_car_brand,
            uv.user_car_model,
            uv.age,
            uv.user_sex,
            uv.user_location,
            COALESCE(SUM(COALESCE(dsi.app_rapid_acc, 0)), 0) as total_rapid_acc,
            COALESCE(SUM(COALESCE(dsi.app_rapid_deacc, 0)), 0) as total_rapid_deacc,
            COALESCE(SUM(COALESCE(dd.gaze_closure, 0)), 0) as total_gaze_closure,
            COUNT(DISTINCT ds.session_id) as session_count
        FROM driving_session ds
        LEFT JOIN uservehicle uv ON ds.car_id = uv.car_id
        LEFT JOIN driving_session_info dsi ON ds.session_id = dsi.session_id
        LEFT JOIN drowsy_drive dd ON ds.session_id = dd.session_id
        WHERE dsi.createdDate IS NOT NULL
        GROUP BY YEAR(dsi.createdDate), MONTH(dsi.createdDate), ds.car_id, uv.user_car_brand, 
                 uv.user_car_model, uv.age, uv.user_sex, uv.user_location
        HAVING session_count > 0
        ORDER BY YEAR(dsi.createdDate) DESC, MONTH(dsi.createdDate) DESC, 
                 (total_rapid_acc + total_rapid_deacc + total_gaze_closure) ASC
    """)
    
    result = db.execute(query)
    rows = result.fetchall()
    
    # 월별로 그룹화하고 각 월별 Top 10 선택
    monthly_data = {}
    for row in rows:
        year = row[0]
        month = row[1]
        key = f"{year}-{month:02d}"
        
        if key not in monthly_data:
            monthly_data[key] = []
        
        total_rapid_acc = row[8] or 0
        total_rapid_deacc = row[9] or 0
        total_gaze_closure = row[10] or 0
        total_score = total_rapid_acc + total_rapid_deacc + total_gaze_closure
        driver_score = max(0, 1000 - (total_score * 10))
        
        monthly_data[key].append({
            "carId": row[2],
            "carBrand": row[3],
            "carModel": row[4],
            "driverAge": row[5],
            "driverSex": row[6],
            "driverLocation": row[7],
            "totalRapidAcc": int(total_rapid_acc),
            "totalRapidDeacc": int(total_rapid_deacc),
            "totalGazeClosure": int(total_gaze_closure),
            "totalScore": int(total_score),
            "driverScore": round(driver_score, 2),
            "sessionCount": row[11]
        })
    
    # 각 월별로 Top 10만 선택
    result_list = []
    for key in sorted(monthly_data.keys(), reverse=True):
        year, month = key.split("-")
        top_10 = monthly_data[key][:10]
        for idx, driver in enumerate(top_10, 1):
            result_list.append({
                "year": int(year),
                "month": int(month),
                "rank": idx,
                **driver
            })
    
    return result_list
