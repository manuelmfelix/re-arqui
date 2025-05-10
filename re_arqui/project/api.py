import os
import django

# Set up Django before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re_arqui.settings")
django.setup()

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status, Header, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import json
from io import StringIO
from pydantic import BaseModel
from django.core.files import File as DjangoFile
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
import shutil

# Import models from Django
from .models import Project, Photo

# Check if we're in production by looking for the production settings module
is_production = os.environ.get("DJANGO_SETTINGS_MODULE") == "re_arqui.settings_prod"

# FastAPI instance with production-appropriate configuration
if is_production:
    # In production, FastAPI is expected to be accessed at /api prefix due to Nginx configuration
    app = FastAPI(title="RE-ARQUI API", root_path="/api")
else:
    # In development, FastAPI is accessed directly
    app = FastAPI(title="RE-ARQUI API")

# Authentication scheme
security = HTTPBearer()

# Pydantic models for API
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    client: Optional[str] = None
    project_year: Optional[int] = None
    construction_year: Optional[int] = None
    architect: Optional[str] = None
    builder: Optional[str] = None
    site: Optional[str] = None
    public_private_project: Optional[int] = 0
    other: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    client: Optional[str] = None
    architect: Optional[str] = None
    builder: Optional[str] = None
    site: Optional[str] = None
    public_private_project: Optional[int] = None

class ProjectResponse(ProjectBase):
    id: int
    
    class Config:
        from_attributes = True

class PhotoBase(BaseModel):
    title: str
    index: Optional[int] = None
    is_cover_image: bool = False
    project_id: int

class PhotoResponse(PhotoBase):
    id: int
    image_url: str
    
    class Config:
        from_attributes = True

# Synchronous function to get a user from token
def get_user_from_token(token_value):
    from rest_framework.authtoken.models import Token
    try:
        token_obj = Token.objects.get(key=token_value)
        return token_obj.user
    except Exception as e:
        return None

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token_value = credentials.credentials
    user = await sync_to_async(get_user_from_token)(token_value)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Routes that don't require authentication
@app.get("/projects/list/", response_model=List[ProjectResponse])
async def list_projects():
    projects = await sync_to_async(list)(Project.objects.all())
    return projects

@app.get("/projects/{project_id}/photos/", response_model=List[PhotoResponse])
async def get_project_photos(project_id: int):
    @sync_to_async
    def get_photos():
        try:
            project = Project.objects.get(id=project_id)
            photos = project.photo_set.all()
            
            # Manually construct response with image URLs
            result = []
            for photo in photos:
                photo_data = {
                    "id": photo.id,
                    "title": photo.title,
                    "index": photo.index,
                    "is_cover_image": photo.is_cover_image,
                    "project_id": photo.project_id,
                    "image_url": photo.image.url if photo.image else None
                }
                result.append(photo_data)
            
            return result
        except Project.DoesNotExist:
            return None
    
    photos = await get_photos()
    if photos is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return photos

# Routes that require authentication
@app.post("/project/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, user: User = Depends(get_current_user)):
    @sync_to_async
    def create_project_sync():
        return Project.objects.create(
            name=project.name,
            description=project.description,
            client=project.client,
            project_year=project.project_year,
            construction_year=project.construction_year,
            architect=project.architect,
            builder=project.builder,
            site=project.site,
            public_private_project=project.public_private_project,
            other=project.other
        )
    
    new_project = await create_project_sync()
    return new_project

@app.post("/photos/")
async def create_photo(
    title: str = Form(...),
    project_id: int = Form(...),
    is_cover_image: bool = Form(False),
    index: Optional[int] = Form(None),
    image: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    # Read file content
    content = await image.read()
    filename = image.filename
    
    @sync_to_async
    def create_photo_sync():
        try:
            project = Project.objects.get(id=project_id)
            
            # Create a temporary file to save the uploaded file
            import tempfile
            import os
            
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            try:
                # Write content to temporary file
                temp_file.write(content)
                temp_file.flush()
                
                # Create Photo with Django File
                photo = Photo.objects.create(
                    title=title,
                    project=project,
                    is_cover_image=is_cover_image,
                    index=index
                )
                
                # Open the temporary file and assign it to the ImageField
                with open(temp_file.name, 'rb') as f:
                    photo.image.save(filename, DjangoFile(f), save=True)
                    
                return {"id": photo.id, "title": photo.title, "image_url": photo.image.url}
            finally:
                temp_file.close()
                os.unlink(temp_file.name)
                
        except Project.DoesNotExist:
            return None
    
    result = await create_photo_sync()
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return result

@app.post("/photos/batch/")
async def create_photos_batch(photos_data: List[dict] = Body(...), user: User = Depends(get_current_user)):
    """
    Upload multiple photos at once from local file paths.
    """
    @sync_to_async
    def process_photos_sync(photos_data):
        results = []
        errors = []
        
        for i, photo_data in enumerate(photos_data):
            try:
                # Check if required fields exist
                if not all(key in photo_data for key in ["title", "image_path"]):
                    errors.append({"index": i, "error": "Missing required fields: title, image_path"})
                    continue
                
                # Find project - first look by name in catalog field if provided
                project = None
                if "catalog" in photo_data and photo_data["catalog"]:
                    try:
                        project = Project.objects.get(name=photo_data["catalog"])
                    except Project.DoesNotExist:
                        pass
                
                # If no project found by catalog, use project_id if provided
                if project is None and "project_id" in photo_data and photo_data["project_id"]:
                    try:
                        project = Project.objects.get(id=photo_data["project_id"])
                    except Project.DoesNotExist:
                        errors.append({"index": i, "error": f"Project not found: {photo_data.get('catalog', '')} or ID: {photo_data.get('project_id', '')}"})
                        continue
                
                if project is None:
                    errors.append({"index": i, "error": "No valid project specified. Provide either catalog (project name) or project_id"})
                    continue
                
                # Check if image path exists
                image_path = photo_data["image_path"]
                if not os.path.exists(image_path):
                    errors.append({"index": i, "error": f"Image file not found: {image_path}"})
                    continue
                
                # Create photo object
                photo = Photo.objects.create(
                    title=photo_data["title"],
                    project=project,
                    is_cover_image=photo_data.get("is_cover_image", False),
                    index=photo_data.get("index", None)
                )
                
                # Copy the image file to Django's media storage
                with open(image_path, 'rb') as src_file:
                    filename = os.path.basename(image_path)
                    photo.image.save(filename, DjangoFile(src_file), save=True)
                
                results.append({
                    "id": photo.id,
                    "title": photo.title,
                    "project_id": project.id,
                    "project_name": project.name,
                    "image_url": photo.image.url
                })
                
            except Exception as e:
                errors.append({"index": i, "error": str(e)})
        
        return {"results": results, "errors": errors}
    
    result = await process_photos_sync(photos_data)
    return result

@app.put("/projects/{project_id}/", response_model=ProjectResponse)
async def update_project(
    project_id: int, 
    project_update: ProjectUpdate, 
    user: User = Depends(get_current_user)
):
    @sync_to_async
    def update_project_sync():
        try:
            project = Project.objects.get(id=project_id)
            
            # Update fields if provided
            update_data = project_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(project, key, value)
            
            project.save()
            return project
        except Project.DoesNotExist:
            return None
    
    updated_project = await update_project_sync()
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

@app.delete("/projects/delete/")
async def delete_all_projects(user: User = Depends(get_current_user)):
    @sync_to_async
    def delete_all_sync():
        return Project.objects.all().delete()
    
    await delete_all_sync()
    return {"message": "All projects deleted successfully"}

@app.delete("/projects/delete/{project_id}/")
async def delete_project(project_id: int, user: User = Depends(get_current_user)):
    @sync_to_async
    def delete_project_sync():
        try:
            project = Project.objects.get(id=project_id)
            project.delete()
            return True
        except Project.DoesNotExist:
            return False
    
    success = await delete_project_sync()
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": f"Project {project_id} deleted successfully"}

# CSV Import/Export functionality simplified without pandas
@app.post("/projects/import-csv/")
async def import_projects_csv(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    contents = await file.read()
    csv_string = contents.decode('utf-8')
    
    @sync_to_async
    def import_csv_sync():
        try:
            # Define a custom CSV parser function
            def parse_csv_line(line):
                result = []
                current_field = ""
                in_quotes = False
                i = 0
                
                while i < len(line):
                    char = line[i]
                    
                    # Handle quotes
                    if char == '"':
                        # Toggle quote state
                        in_quotes = not in_quotes
                        
                        # Handle escaped quotes (double quotes)
                        if i + 1 < len(line) and line[i+1] == '"':
                            current_field += '"'
                            i += 2
                            continue
                    
                    # Handle commas
                    elif char == ',' and not in_quotes:
                        # End of field
                        result.append(current_field)
                        current_field = ""
                        i += 1
                        continue
                    
                    # Add character to current field
                    current_field += char
                    i += 1
                
                # Add the last field
                result.append(current_field)
                return result
            
            # Split the CSV into lines, accounting for newlines in quotes
            def split_csv_lines(text):
                lines = []
                current_line = ""
                in_quotes = False
                
                for char in text:
                    if char == '"':
                        in_quotes = not in_quotes
                    
                    # Only split on newlines outside of quotes
                    if char == '\n' and not in_quotes:
                        lines.append(current_line)
                        current_line = ""
                    else:
                        current_line += char
                
                # Add the last line if it's not empty
                if current_line:
                    lines.append(current_line)
                
                return lines
            
            # Process the CSV
            lines = split_csv_lines(csv_string)
            if not lines:
                return {"error": "Empty CSV file"}
            
            # Parse headers
            headers = parse_csv_line(lines[0])
            
            # Validate required columns
            required_columns = ['name', 'client', 'architect', 'builder', 'site']
            for col in required_columns:
                if col not in headers:
                    return {"error": f"Missing required column: {col}"}
            
            # Create projects from CSV
            projects_created = []
            for line_idx in range(1, len(lines)):
                line = lines[line_idx]
                if not line.strip():  # Skip empty lines
                    continue
                
                values = parse_csv_line(line)
                project_data = {}
                
                for j, header in enumerate(headers):
                    if j < len(values) and values[j].strip():
                        if header in ['project_year', 'construction_year', 'public_private_project']:
                            try:
                                project_data[header] = int(values[j])
                            except ValueError:
                                # If not a valid integer, skip this field
                                continue
                        else:
                            project_data[header] = values[j]
                
                # Ensure required fields are present
                if all(field in project_data for field in required_columns):
                    try:
                        project = Project.objects.create(**project_data)
                        projects_created.append(project.id)
                    except Exception as e:
                        print(f"Error creating project on line {line_idx+1}: {str(e)}")
                        print(f"Data: {project_data}")
                else:
                    missing = [field for field in required_columns if field not in project_data]
                    print(f"Skipping line {line_idx+1}, missing fields: {missing}")
                    print(f"Available data: {project_data}")
            
            return {"message": f"Successfully imported {len(projects_created)} projects", "project_ids": projects_created}
        
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return {"error": f"Error importing CSV: {str(e)}"}
    
    result = await import_csv_sync()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/projects/export-csv/")
async def export_projects_csv(user: User = Depends(get_current_user)):
    @sync_to_async
    def export_csv_sync():
        import csv
        from io import StringIO
        
        projects = Project.objects.all()
        
        # Create CSV using csv module
        output = StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        headers = ['id', 'name', 'description', 'client', 'project_year', 'construction_year', 
                'architect', 'builder', 'site', 'public_private_project', 'other']
        
        writer.writerow(headers)
        
        for project in projects:
            row = [
                str(project.id),
                project.name,
                project.description or '',
                project.client,
                str(project.project_year) if project.project_year else '',
                str(project.construction_year) if project.construction_year else '',
                project.architect,
                project.builder,
                project.site,
                str(project.public_private_project),
                project.other or ''
            ]
            writer.writerow(row)
        
        return output.getvalue()
    
    csv_content = await export_csv_sync()
    
    from fastapi.responses import Response
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=projects.csv"}
    ) 