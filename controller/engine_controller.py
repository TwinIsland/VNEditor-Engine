from functools import partial
from module.config_module import ConfigLoader
from utils.status import StatusCode
from utils.return_type import ReturnList, ReturnDict, ReturnStatus
from utils.exception_handler import exception_handler
from .project_controller import Task
from kernel.frame import FrameModel, frame_to_model, make_frame, make_empty_frame

engine_controller_exception_handler = partial(
    exception_handler, module_name="Engine Controller", debug=True
)


class EngineController:
    """
    class for kernel controller

    """

    def __init__(self, config_dir: str):
        """
        constructor for router class

        """
        config_loader = ConfigLoader(config_dir=config_dir)
        self.__engine_config: dict = config_loader.engine()

    @engine_controller_exception_handler
    def get_frame_ids(self, task: Task, chapter_name: str) -> ReturnList:
        """
        get all frame ids

        @param chapter_name:
        @param task:
        @return: list of ordered frame id

        """
        engine = task.project_engine
        fids = engine.get_chapter(chapter_name).get_all_fid()
        return ReturnList(status=StatusCode.OK, content=fids)

    @engine_controller_exception_handler
    def get_frame_names(self, task: Task, chapter_name: str):
        """
        get all frame names

        @param chapter_name:
        @param task: cur task
        @return: list of ordered frame names

        """
        engine = task.project_engine
        fids = engine.get_chapter(chapter_name).get_all_fid()
        names = [engine.get_frame_name(i) for i in fids]
        return ReturnList(status=StatusCode.OK, content=names)

    @engine_controller_exception_handler
    def get_engine_meta(self, task: Task) -> ReturnDict:
        """
        get the metadata for kernel

        @return: metadata for kernel

        """
        engine = task.project_engine
        return ReturnDict(status=StatusCode.OK, content=engine.get_engine_meta())

    @engine_controller_exception_handler
    def append_frame(self, task: Task, to_chapter: str, frame_name: str) -> ReturnList:
        """
        append an empty frame according to chapter

        @param frame_name: name for the chapter
        @param to_chapter: append to which chapter
        @param task:
        @return: the added frame id

        """
        engine = task.project_engine
        empty_frame = make_empty_frame(frame_name)
        fid = engine.append_frame(empty_frame, to_chapter, force=True)
        engine.commit()
        return ReturnList(
            status=StatusCode.OK, msg="successfully add frame", content=[fid]
        )

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
        frame_component = frame_component_raw.to_frame().__dict__
        frame = make_frame(**frame_component)
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
        frame_model = frame_to_model(frame_raw)
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
        engine.commit()
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
    def render_struct(self, task: Task, chapter_name: str = None) -> ReturnDict:
        """
        Render and return the project struct

        @param chapter_name: filter by specific chapter
        @param task: current task
        @return: struct

        """
        engine = task.project_engine
        struct = engine.render_struct(by_chapter=chapter_name)
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
        engine.add_chapter(chapter_name)
        engine.commit()
        return ReturnStatus(status=StatusCode.OK, msg="chapter added")

    @engine_controller_exception_handler
    def remove_chapter(self, task: Task, chapter_name: str) -> ReturnStatus:
        """
        remove the whole chapter include the frames under it

        @param task: the task instance
        @param chapter_name: the name for chapter to be removed
        @return: ok or not

        """
        engine = task.project_engine
        try:
            engine.remove_chapter(chapter_name)
            engine.commit()
            return ReturnStatus(
                status=StatusCode.OK,
                msg=f"the chapter '{chapter_name}' has been removed",
            )
        except Exception as e:
            engine.rollback()
            raise e
