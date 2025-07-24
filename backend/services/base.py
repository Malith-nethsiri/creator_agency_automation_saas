from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from pydantic import BaseModel
from core.utils import paginate_query, APIException
from fastapi import HTTPException, status

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_or_404(self, id: Any) -> ModelType:
        """Get a single record by ID or raise 404"""
        obj = self.get(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )
        return obj

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering"""
        query = self.db.query(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

        return query.offset(skip).limit(limit).all()

    def get_paginated(
        self,
        page: int = 1,
        per_page: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get paginated results"""
        query = self.db.query(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

        return paginate_query(query, page, per_page)

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record"""
        update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, *, id: Any) -> ModelType:
        """Delete a record by ID"""
        obj = self.get_or_404(id)
        self.db.delete(obj)
        self.db.commit()
        return obj

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering"""
        query = self.db.query(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

        return query.count()
