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
from source.config.api_config import *

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    openapi_tags=TAGS_METADATA,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=get_openapi_url(),
    contact=CONTACT_INFO,
    license_info=LICENSE_INFO,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
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
@app.get(
    f"{API_PREFIX}/health",
    response_model=HealthCheckModel,
    tags=["Health"],
    summary="Health Check",
    description="Check if the API service is running and healthy",
    responses={
        200: {
            "description": "Service is healthy and operational",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2025-10-24T10:00:00+07:00",
                        "service": "Case Similarity Processing API"
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    Health check endpoint
    
    Returns the current health status of the API service including:
    - Service status
    - Current timestamp
    - Service name
    """
    return HealthCheckModel(
        status="healthy",
        timestamp=datetime.now(pytz.timezone(TIMEZONE)),
        service=API_TITLE
    )@app.post(
    f"{API_PREFIX}/process-case",
    response_model=ProcessingResponseModel,
    tags=["Case Processing"],
    summary="Process Case Synchronously",
    description="Process case data to find similarities and create or update cases",
    responses={
        200: {
            "description": "Case processed successfully",
        },
        422: {
            "description": "Validation error in input data",
        },
        500: {
            "description": "Internal server error during processing",
        }
    }
)
async def process_case(case_data: InputDataModel):
    """
    Process case data to find similarities and create or update cases
    
    This endpoint processes case data synchronously and returns the result immediately.
    
    **Process Flow:**
    1. Validates input data
    2. Searches for similar cases based on embeddings and filters
    3. Creates a new case or updates an existing one
    4. Returns processing results with similarity information
    
    **Parameters:**
    - **case_data**: Input data containing case information, thresholds, and filters
    
    **Returns:**
    - Processing status
    - Case ID and Data ID
    - Number of similar cases found
    - Processing time
    - Whether a new case was created
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

@app.post(
    f"{API_PREFIX}/process-case-async",
    tags=["Case Processing"],
    summary="Process Case Asynchronously",
    description="Process case data asynchronously in the background and return immediately",
    responses={
        200: {
            "description": "Background processing task started",
            "content": {
                "application/json": {
                    "example": {
                        "status": "accepted",
                        "message": "Case processing started in background",
                        "task_id": "task_20251024_100000",
                        "radius_coordinate": 500.0,
                        "score_threshold": 0.7
                    }
                }
            }
        },
        500: {
            "description": "Failed to start background processing",
        }
    }
)
async def process_case_async(case_data: InputDataModel, background_tasks: BackgroundTasks):
    """
    Process case data asynchronously in the background
    
    This endpoint accepts case data and starts processing in the background,
    returning immediately with a task ID for tracking.
    
    **Use Case:**
    - Large batch processing
    - Non-urgent case analysis
    - Preventing timeout on slow operations
    
    **Parameters:**
    - **case_data**: Input data containing case information
    - **background_tasks**: FastAPI background tasks handler (auto-injected)
    
    **Returns:**
    - Task ID for tracking
    - Processing parameters
    - Status confirmation
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

@app.get(
    f"{API_PREFIX}/find-similar",
    response_model=List[SimilarDataModel],
    tags=["Search"],
    summary="Find Similar Cases",
    description="Search for similar cases based on text, location, and temporal filters",
    responses={
        200: {
            "description": "List of similar cases found",
        },
        500: {
            "description": "Error during search operation",
        }
    }
)
async def find_similar_cases(
    text: str = Query(..., description="Text to find similar cases for"),
    coordinate_lat: Optional[float] = Query(None, description="Latitude for location filtering"),
    coordinate_lon: Optional[float] = Query(None, description="Longitude for location filtering"),
    timestamp: Optional[int] = Query(None, description="Unix timestamp for time filtering"),
    subdistrict_code: Optional[str] = Query(None, description="Subdistrict code for filtering"),
    coordinate_max_radius: Optional[float] = Query(500.0, description="Maximum radius for coordinate search (in meters)"),
    score_threshold: Optional[float] = Query(0.0, description="Minimum similarity score threshold (0.0 to 1.0)"),
    limit: Optional[int] = Query(10, description="Maximum number of results to return")
):
    """
    Find similar cases based on text and optional filters
    
    This endpoint searches for cases similar to the provided text using vector embeddings,
    with optional filtering by location, time, and administrative regions.
    
    **Search Capabilities:**
    - **Text Similarity**: Uses vector embeddings for semantic similarity
    - **Location Filter**: Filter by coordinates with configurable radius
    - **Time Filter**: Filter by timestamp
    - **Region Filter**: Filter by subdistrict code
    
    **Parameters:**
    - **text**: The query text to search for (required)
    - **coordinate_lat/lon**: GPS coordinates for location-based filtering
    - **coordinate_max_radius**: Search radius in meters (default: 500m)
    - **timestamp**: Unix timestamp for temporal filtering
    - **subdistrict_code**: Administrative region code
    - **score_threshold**: Minimum similarity score (0.0-1.0)
    - **limit**: Maximum results to return
    
    **Returns:**
    - List of similar cases with scores and metadata
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

@app.post(
    f"{API_PREFIX}/report/latest",
    response_model=LatestReportResponse,
    tags=["Reports"],
    summary="Get Latest Report by Case ID",
    description="Retrieve the most recent report for a specific case with optional time filtering",
    responses={
        200: {
            "description": "Latest report found and returned",
        },
        404: {
            "description": "No reports found for the specified case ID",
        },
        422: {
            "description": "Invalid time format in request",
        },
        500: {
            "description": "Error retrieving report",
        }
    }
)
async def get_latest_report(request: GetLatestReportRequest):
    """
    Get the latest report for a specific case_id with optional time filtering using Qdrant
    
    This endpoint retrieves the most recent report for a given case ID, with optional
    filtering by time range.
    
    **Features:**
    - Get latest report by case ID
    - Optional time range filtering
    - Sorted by most recent first
    - Includes full report metadata
    
    **Parameters:**
    - **case_id**: The ID of the case to retrieve reports for (required)
    - **start_time**: Optional start time filter (format: YYYY-MM-DD HH:MM:SS +ZZZZ)
    - **end_time**: Optional end time filter (format: YYYY-MM-DD HH:MM:SS +ZZZZ)
    - **limit**: Maximum number of reports to retrieve (default: 10)
    
    **Returns:**
    - Latest report details
    - Total reports found
    - Query parameters used
    
    **Example Time Format:**
    ```
    2025-10-24 10:00:00 +0700
    ```
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

@app.get(
    "/",
    tags=["Information"],
    summary="API Information",
    description="Get general API information and available endpoints",
    responses={
        200: {
            "description": "API information and endpoint list",
        }
    }
)
async def root():
    """
    Root endpoint with API information
    
    Returns general information about the API including:
    - API name and version
    - Available endpoints
    - Documentation links
    """
    return {
        "message": "Case Similarity Processing API",
        "version": API_VERSION,
        "api_prefix": API_PREFIX,
        "endpoints": {
            f"{API_PREFIX}/health": "Health check",
            f"{API_PREFIX}/process-case": "Process case data synchronously",
            f"{API_PREFIX}/process-case-async": "Process case data asynchronously",
            f"{API_PREFIX}/find-similar": "Find similar cases",
            f"{API_PREFIX}/report/latest": "Get latest report by case ID (POST)",
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "Alternative API documentation (ReDoc)"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": f"{API_PREFIX}/openapi.json"
        },
        "support": {
            "email": "support@example.com",
            "documentation": "See /docs for detailed API documentation"
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
    
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")
    logger.info(f"API Prefix: {API_PREFIX}")
    logger.info(f"Documentation available at: http://{SERVER_HOST}:{SERVER_PORT}{DOCS_URL}")
    
    uvicorn.run(
        "api:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=SERVER_RELOAD,
        log_level=LOG_LEVEL.lower()
    )