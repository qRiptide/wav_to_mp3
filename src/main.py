import os
import uuid
import uvicorn

from pathlib import PurePath
from typing import Annotated

from fastapi import FastAPI, Body, UploadFile, Request, Depends
from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.models import User, Mp3Record
from src.utils import clean_convert

app = FastAPI(title='wav-to-mp3 App', version='0.1:beta', debug=False)
records_dir = PurePath(os.getenv('RECORDS_PATH'))


@app.post('/user', status_code=status.HTTP_201_CREATED)
async def regiser(username: Annotated[str, Body()],
                  db_session: AsyncSession = Depends(get_db_session)
                  ):
    user = await User.create_user(db_session, username)

    return {'id': user.id, 'uuid': user.uuid}


@app.post('/record')
async def convert_record(user_id: Annotated[int, Body()],
                         user_uuid: Annotated[uuid.UUID, Body()],
                         wav_record: UploadFile,
                         request: Request,
                         db_session: AsyncSession = Depends(get_db_session)
                         ):
    if wav_record.content_type != 'audio/wav':
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File format must be WAV"
        )

    user = await User.select_user_by_id_uuid(db_session, user_id, user_uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist, please register"
        )

    user_uuid = str(user_uuid)
    mp3_uuid = uuid.uuid4()
    mp3_str_uuid = str(mp3_uuid)
    path_to_db = PurePath(user_uuid, mp3_str_uuid + '.mp3')

    record_id = await Mp3Record.insert_mp3_returning_id(db_session,
                                                        user_id,
                                                        mp3_uuid,
                                                        path_to_db
                                                        )

    records_path = records_dir / user_uuid
    clean_convert(wav_record, records_path, mp3_str_uuid + '.mp3')

    params = request.url._url, record_id, user_id  # noqa
    return {'download_url': '%s?record_id=%s&user_id=%s' % params}


@app.get('/record')
async def download_record(user_id: int,
                          record_id: int,
                          db_session: AsyncSession = Depends(get_db_session)
                          ):
    record_path = await Mp3Record.select_audio(db_session, user_id, record_id)
    if record_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record is missing"
        )

    filepath = records_dir / record_path.path
    return FileResponse(filepath)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
