from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import logging
import pytz
import sys
from pathlib import Path

# Add parent directory to path to import from root
path_this = Path(__file__).resolve().parent
path_project = path_this.parent
path_root = path_project.parent
sys.path.append(str(path_root))

# Import your processor class
from source.case_similarity import CaseSimilarityProcessor
from source.models.api_models import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Case Similarity Processing API",
    description="API for processing and finding similar cases using vector embeddings",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize processor
processor = CaseSimilarityProcessor()

# Background task for processing
async def process_case_background(case_data: dict, task_id: str, score_threshold: float, limit: int, radius_coordinate: float, report_type: Optional[str] = None):
    """Background task to process case data"""
    try:
        logger.info(f"Starting background processing for task {task_id}")
        result = await processor.process_data(case_data, score_threshold=score_threshold, limit=limit, radius_coordinate=radius_coordinate, report_type=report_type)
        logger.info(f"Background processing completed for task {task_id}: {result}")
        return result
    except Exception as e:
        logger.error(f"Background processing failed for task {task_id}: {e}")
        return False

# API Endpoints
@app.get("/health", response_model=HealthCheckModel)
async def health_check():
    """Health check endpoint"""
    return HealthCheckModel(
        status="healthy",
        timestamp=datetime.now(pytz.timezone("Asia/Jakarta")),
        service="Case Similarity Processing API"
    )

@app.post("/process-case", response_model=ProcessingResponseModel)
async def process_case(case_data: InputDataModel):
    """
    Process case data to find similarities and create or update cases
    """
    start_time = datetime.now()
    
    try:
        # Convert Pydantic model to dict
        case_dict = case_data.data.dict()
        score_threshold = case_data.score_threshold
        limit = case_data.limit
        radius_coordinate = case_data.radius_coordinate
        report_type = case_data.report_type

        logger.info(f"Processing case data for input: {case_data.data.input[:50]}...")
        
        # Process the data
        result, len_sim_data = await processor.process_data(case_dict, score_threshold=score_threshold, limit=limit, report_type=report_type, radius_coordinate=radius_coordinate)
        
        if result:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Try to extract case_id and data_id from the processed data
            # You might want to modify your processor to return more detailed info
            return ProcessingResponseModel(
                status=ProcessingStatusEnum.SUCCESS,
                message="Case processed successfully",
                case_id=result.get("id_case"),
                data_id=result.get("id"),
                similar_cases_count=len_sim_data,
                score_threshold=score_threshold,
                radius_coordinate=radius_coordinate,
                is_new_case=True if len_sim_data == 0 else False,
                processing_time=processing_time,
                case_name=result.get("case_name")
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to process case data"
            )
            
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/process-case-async")
async def process_case_async(case_data: InputDataModel, background_tasks: BackgroundTasks):
    """
    Process case data asynchronously in the background
    """
    try:
        # Convert Pydantic model to dict
        case_dict = case_data.data.dict()
        score_threshold = case_data.score_threshold
        radius_coordinate = case_data.radius_coordinate
        limit = case_data.limit

        # Generate a task ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Add background task
        background_tasks.add_task(process_case_background, case_dict, task_id, score_threshold, limit, radius_coordinate, case_data.report_type)
        
        return {
            "status": "accepted",
            "message": "Case processing started in background",
            "task_id": task_id,
            "radius_coordinate": radius_coordinate,
            "score_threshold": score_threshold
        }
        
    except Exception as e:
        logger.error(f"Error starting background task: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start background processing: {str(e)}"
        )

@app.get("/find-similar", response_model=List[SimilarDataModel])
async def find_similar_cases(
    text: str = Query(..., description="Text to find similar cases for"),
    coordinate_lat: Optional[float] = Query(None, description="Latitude for location filtering"),
    coordinate_lon: Optional[float] = Query(None, description="Longitude for location filtering"),
    timestamp: Optional[int] = Query(None, description="Unix timestamp for time filtering"),
    subdistrict_code: Optional[str] = Query(None, description="Subdistrict code for filtering"),
    coordinate_max_radius: Optional[float] = Query(500.0, description="Maximum radius for coordinate search"),
    score_threshold: Optional[float] = Query(0.0, description="Score threshold for filtering"),
    limit: Optional[int] = Query(10, description="Maximum number of results to return")
):
    """
    Find similar cases based on text and optional filters
    """
    try:
        # Create coordinate dict if provided
        coordinate = None
        if coordinate_lat is not None and coordinate_lon is not None:
            coordinate = {"lat": coordinate_lat, "lon": coordinate_lon}
        
        # Create filter
        qdrant_filter = processor._create_qdrant_filter(
            coordinate=coordinate,
            timestamp=timestamp,
            subdistrict_code=subdistrict_code,
            coordinate_max_radius=coordinate_max_radius
        )
        
        # Find similar data
        similar_data = await processor._find_similar_data(
            text=text,
            qdrant_filter=qdrant_filter,
            score_threshold=score_threshold,
            limit=limit
        )
        
        if similar_data is None:
            return []
        
        return [SimilarDataModel(**item) for item in similar_data]
        
    except Exception as e:
        logger.error(f"Error finding similar cases: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find similar cases: {str(e)}"
        )

@app.post("/report/latest", response_model=LatestReportResponse)
async def get_latest_report(request: GetLatestReportRequest):
    """
    Get the latest report for a specific case_id with optional time filtering using Qdrant
    """
    try:
        logger.info(f"Getting latest report for case_id: {request.case_id}")
        
        # Parse time filters if provided
        start_timestamp = None
        end_timestamp = None
        query_time_range = {}
        
        if request.start_time:
            try:
                start_dt = datetime.strptime(request.start_time, "%Y-%m-%d %H:%M:%S %z")
                start_timestamp = int(start_dt.timestamp())
                query_time_range["start_time"] = request.start_time
            except ValueError:
                raise HTTPException(
                    status_code=422,
                    detail="start_time must be in format: YYYY-MM-DD HH:MM:SS +ZZZZ"
                )
        
        if request.end_time:
            try:
                end_dt = datetime.strptime(request.end_time, "%Y-%m-%d %H:%M:%S %z")
                end_timestamp = int(end_dt.timestamp())
                query_time_range["end_time"] = request.end_time
            except ValueError:
                raise HTTPException(
                    status_code=422,
                    detail="end_time must be in format: YYYY-MM-DD HH:MM:SS +ZZZZ"
                )
        
        # Get reports using Qdrant
        reports = await processor.get_reports_by_case_id(
            case_id=request.case_id,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=request.limit
        )
        
        if not reports:
            raise HTTPException(
                status_code=404,
                detail=f"No reports found for case_id '{request.case_id}'"
            )
        
        # Sort by timestamp (most recent first) and get the latest
        sorted_reports = sorted(reports, key=lambda x: x.get("timestamp", 0), reverse=True)
        latest_report = sorted_reports[0]
        
        # Convert to ReportModel
        latest_report_model = ReportModel(
            id=latest_report.get("id", ""),
            case_id=latest_report.get("id_case", request.case_id),
            report_text=latest_report.get("input", ""),
            created_at=latest_report.get("created_at", ""),
            processed_at=latest_report.get("processed_at"),
            metadata=latest_report
        )
        
        return LatestReportResponse(
            case_id=request.case_id,
            reports_found=len(reports),
            latest_report=latest_report_model,
            query_time_range=query_time_range if query_time_range else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest report for case_id {request.case_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get latest report: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Case Similarity Processing API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/process-case": "Process case data synchronously",
            "/process-case-async": "Process case data asynchronously",
            "/find-similar": "Find similar cases",
            "/report/latest": "Get latest report by case ID (POST)",
            "/docs": "API documentation"
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponseModel(
            message=str(exc.detail),
            error_code=str(exc.status_code)
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponseModel(
            message="Internal server error",
            error_code="500"
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",  # Change this to your filename if different
        host="0.0.0.0",
        port=8000,
        # reload=True,
        log_level="info"
    )