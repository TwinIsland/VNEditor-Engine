from functools import wraps

from module.config_manager import ConfigLoader
from utils.status import StatusCode
from utils.return_type import ReturnList, ReturnDict, ReturnStatus

from .project_controller import Task
from engine.frame import FrameModel, frame_to_model


def engine_controller_exception_handler(func):
    """
    exception decorator for router

    @param func: function to be decorated

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            e_msg = f"Engine Controller ({type(e).__name__}): {str(e)}"
            print(e_msg)
            return ReturnStatus(status=StatusCode.FAIL, msg=e_msg)

    wrapper: func
    return wrapper


class EngineController:
    """
    class for engine controller

    """

    def __init__(self, config_dir: str):
        """
        constructor for router class

        """
        config_loader = ConfigLoader(config_dir=config_dir)
        self.__engine_config: dict = config_loader.engine()

    @engine_controller_exception_handler
    def get_frames_id(self, task: Task) -> ReturnList:
        """
        get all frame id

        @param task:
        @return: list of ordered frame id

        """
        engine = task.project_engine
        fids = engine.get_ordered_fid()

        return ReturnList(status=StatusCode.OK, content=fids)

    @engine_controller_exception_handler
    def get_engine_meta(self, task: Task) -> ReturnDict:
        """
        get the metadata for engine

        @return: metadata for engine

        """
        engine = task.project_engine
        return ReturnDict(status=StatusCode.OK, content=engine.get_engine_meta())

    @engine_controller_exception_handler
    def append_empty_frame(self, task: Task, to_chapter: str):
        """
        append an empty frame according to chapter

        @param to_chapter: append to which chapter
        @param task:
        @return: the added frame id

        """
        pass

    @engine_controller_exception_handler
    def modify_frame(
        self, task: Task, fid: int, frame_component_raw: FrameModel
    ) -> ReturnStatus:
        """
        commit all changes

        @param frame_component_raw: raw content of frame
        @param fid: the frame id
        @param task: current task
        @return: status

        """
        engine = task.project_engine
        frame_component = frame_component_raw.to_frame()[0].__dict__
        frame_component.pop("fid")
        frame_component.pop("action")
        frame = engine.make_frame(**frame_component)
        engine.change_frame(fid, frame)
        engine.commit()
        return ReturnStatus(status=StatusCode.OK)

    @engine_controller_exception_handler
    def get_frame(self, task: Task, fid: int) -> ReturnDict:
        """
        get the frame information

        @return: content of frame with given id

        """
        engine = task.project_engine
        if engine.check_frame_exist(fid) is None:
            return ReturnDict(status=StatusCode.FAIL, msg=f"No such frame id '{fid}'")

        frame_raw = engine.get_frame(fid=fid)
        frame_meta = engine.get_frame_meta(fid=fid)
        frame_model = frame_to_model(frame_raw, frame_meta)
        return ReturnDict(content=frame_model.__dict__)

    @engine_controller_exception_handler
    def remove_frame(self, task: Task, fid: int) -> ReturnList:
        """
        remove the frame with given fid

        @return: the removed fid
        """
        engine = task.project_engine
        if engine.check_frame_exist(fid) is None:
            return ReturnList(status=StatusCode.FAIL, msg=f"No such frame id '{fid}'")

        engine.remove_frame(fid)
        return ReturnList(
            status=StatusCode.OK,
            msg=f"successfully remove frame with id '{fid}'",
            content=[fid],
        )

    @engine_controller_exception_handler
    def get_metadata(self, task: Task) -> ReturnDict:
        """
        get game content metadata buffer

        @param task: current task
        @return: status

        """
        engine = task.project_engine
        meta_buffer = engine.get_metadata_buffer()
        return ReturnDict(status=StatusCode.OK, content=meta_buffer)

    @engine_controller_exception_handler
    def render_struct(self, task: Task, chapter=None) -> ReturnDict:
        """
        Render and return the project struct

        @param chapter: filter by specific chapter
        @param task: current task
        @return: struct

        """
        engine = task.project_engine
        struct = engine.render_struct(chapter=chapter)
        return ReturnDict(status=StatusCode.OK, content=struct)

    @engine_controller_exception_handler
    def get_chapters(self, task: Task) -> ReturnList:
        """
        get all chapters

        @param task: the task instance
        @return: chapter list

        """
        engine = task.project_engine
        return ReturnList(status=StatusCode.OK, content=engine.get_all_chapter())

    @engine_controller_exception_handler
    def add_chapter(self, task: Task, chapter_name: str) -> ReturnStatus:
        """
        add a chapter according to the chapter name given

        @param task: the task instance
        @param chapter_name: the name for chapter
        @return ok or not

        """
        engine = task.project_engine
        engine.append_chapter(engine.make_chapter(chapter_name))
        return ReturnStatus(status=StatusCode.OK, msg="chapter added")
