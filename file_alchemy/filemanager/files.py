import os
import re
from base64 import b64decode
from flask_sqlalchemy import Model
from sqlalchemy import Column, event
from PIL import Image
from file_alchemy.logger import logger


class BaseFileAttach:
    __name__: str
    column: Column
    filename_generator: Column
    model: Model
    prefix: str
    _extensions: set[str]

    @property
    def directory(self):
        return f'{self._filemanager.upload_folder}/{self.__name__}/{self.model.__tablename__}{self._prefix}/'

    def __init__(self):
        raise NotImplementedError()

    def init_filemanager(self, filemanager):
        self._filemanager = filemanager

    def save(self):
        raise NotImplementedError()

    def _insert(self) -> callable:
        raise NotImplementedError()
    
    def _delete(self, mapper, connection, instance) -> None:
        raise NotImplementedError()
    
    def _update(self, mapper, connection, instance) -> None:
        raise NotImplementedError()

class Base64ImageAttach(BaseFileAttach):
    """
    Attach base64-file to sqlalchemy column.
    """
    __name__ = 'images'
    __base64pattern = r'^data:image/.+;base64,'
    __base64type = r'/.+;'
    _extensions = {'png', 'jpg', 'jfif'}

    # TODO: WRITE FILENAME DEFAULT GENERATOR AND ALLOW THROW FUNC TO filename_generator arg
    def __init__(self, column: Column, filename_generator: Column, prefix: str, size: tuple[int, int]|None=None):
        self.column = column
        self.model = column.class_
        self.filename_generator = filename_generator
        self._prefix = prefix
        self._size = size
        """Register sqlalchemy events to attached field"""
        event.listen(self.model, 'init', self._insert)
        event.listen(self.column, 'set', self._set, retval=True)
        event.listen(self.model, 'before_update', self._update)
        event.listen(self.model, 'before_delete', self._delete)

    def __create_file_path(self, filename, image_ext):
        """Create file path"""
        return f'{self.directory}{filename}.{image_ext if image_ext in self._extensions else "jpg"}'

    def save(self, file_path: str, src: str) -> str:
        """Initial saving attached image"""
        image_data = b64decode(re.sub(self.__base64pattern, '', src))
        with open(file_path, 'w+b') as image:
            image.write(image_data)
            size = os.path.getsize(file_path)
            logger.debug(f'File Size is {size/(2**20)} megabytes.')
        self.__optimize(file_path)
        return file_path

    def _insert(self, instance, args, kwargs):
        """Init event handler to proccesing attached file-field"""
        logger.debug(f'Init attached instance {instance}')
        src, filename = kwargs.get(self.column.key), kwargs.get(self.filename_generator.key)
        image_path = self.__create_file_path(filename=filename, image_ext=self.__parse_type(src))
        """Check file path is unique"""
        self.__check_unique_filepath(file_path=image_path, instance=instance)
        kwargs[self.column.key] = self.save(file_path=image_path, src=src)

    def _set(self, target, value, oldvalue, initiator):
        """Set event handler for attached field"""
        logger.debug(f'Set attached field {target}')
        if not self.is_path(value):
            filename = getattr(target, self.filename_generator.key)
            value = self.save(self.__create_file_path(filename, image_ext=self.__parse_type(value)), value)
            if value != oldvalue:
                try:
                    os.remove(oldvalue)
                except ValueError as er:
                    logger.error(f'Remove error: {er}')
        return value

    def is_path(self, path: str) -> bool:
        """Check that value is path like"""
        result = True if os.path.splitext(path.split(':')[0])[-1] else False
        return result

    def _delete(self, mapper, connection, instance) -> None:
        """Delete image before deleting attached field"""
        logger.debug(f'Delete attached file {instance}')
        image = getattr(instance, self.column.key)
        if os.path.isfile(image):
            os.remove(image)
            logger.debug(f'Attached image deleted: {image}')
        else:
            logger.debug(f'Not valid path {image}')
    
    def _update(self, mapper, connection, instance) -> None:
        """Update image before updating attached instance"""
        logger.debug(f'Update attached filename {instance}')
        image = getattr(instance, self.column.key)
        type_extension = os.path.splitext(image)[-1]
        new_path = self.__create_file_path(getattr(instance, self.filename_generator.key), type_extension)
        """Check file path is unique"""
        self.__check_unique_filepath(file_path=new_path, instance=instance)
        setattr(instance, self.column.key, new_path)
        os.rename(image, new_path)
    
    def __parse_type(self, src) -> str:
        """Parse base64 src to get file extension"""
        regex_result = re.search(self.__base64type, src)
        _type = f"{regex_result.group().strip('/ ;')}" if regex_result else 'jpg'
        return _type

    def __optimize(self, image_path: str):
        """Optimize file: resize, optimize file size"""
        logger.debug(f'Optimize attached file {image_path}')
        with Image.open(image_path) as image:
            if self._size:
                image.thumbnail(self._size, Image.LANCZOS) # width, height resize
            image.save(image_path, optimize=True, quality=95) # optimize file size
        size = os.path.getsize(image_path)
        logger.debug(f'File Size is {size/(2**20)} megabytes.') # TODO: get file size
    
    def __check_unique_filepath(self, file_path: str, instance=None) -> None:
        """Check file path is unique"""
        equal_instances = self._filemanager.db.session.query(self.model).filter(self.column==file_path).all()
        for equal_instance in equal_instances:
            if not equal_instance == instance:
                raise ValueError(f'Not unique filename {file_path}')