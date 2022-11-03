from __future__ import annotations
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column
from file_alchemy.filemanager.files import BaseFileAttach
from file_alchemy.logger import logger


class BaseFileManager:
    
    def init_app(self, app: Flask, db: SQLAlchemy) -> BaseFileManager:
        """ Flask style ^v^ """
        raise NotImplementedError()
    
    def attach_field(self) -> None:
        raise NotImplementedError()


class FileManager(BaseFileManager):
    upload_folder: str = 'media'
    _attached_columns: dict[str, BaseFileAttach]
    __prefix_set: set[str]

    def __init__(self, app: Flask|None=None, db: SQLAlchemy|None=None):
        self._attached_columns = {}
        self.__prefix_set = set()
        if app:
            self.init_app(app, db)
    
    def init_app(self, app, db: SQLAlchemy) -> FileManager:
        """ Flask style ^v^ """
        self.upload_folder = app.config.get('UPLOAD_FOLDER', 'media')
        self.db = db
        self.__create_directory(self.upload_folder)
        return self

    def attach_field(self, attacher: BaseFileAttach) -> callable:
        """Register attached fields and returns sqlalchemy validates func"""
        logger.info(f'attach_file {attacher.model}')
        attacher.init_filemanager(self)
        if attacher.directory not in self.__prefix_set:
            if self._attached_columns.get(attacher.model.__tablename__):
                self._attached_columns[attacher.model.__tablename__][attacher.column.key] = attacher
            else:
                self._attached_columns[attacher.model.__tablename__] = {}
                self._attached_columns[attacher.model.__tablename__][attacher.column.key] = attacher
            self.__prefix_set.add(attacher.directory)
            logger.info(attacher.directory)
            self.__create_directory(attacher.directory)
        else:
            raise ValueError(f'Prefix must be unique: {attacher.directory} is not unique')
        return self

    def save(self, column: Column, filename: str, src: str) -> str:
        """Save image at attached field prefix directory"""
        attached_column = self._attached_columns.get(column.class_.__tablename__).get(column.key)
        if attached_column:
            return attached_column.save(filename, src)
        else:
            raise ValueError(f'No attached columns at column: {column}')

    def __create_directory(self, path) -> None:
        """Create directory if doesnt exist"""
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            logger.debug(f'Directory exists f{path}')
