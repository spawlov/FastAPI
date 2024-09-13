from app.api.schemas.todo import ToDoCreate, ToDoFromDB
from app.utils.unitofwork import IUnitOfWork


class ToDoService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_todo(self, todo: ToDoCreate) -> ToDoFromDB:
        todo_dict: dict = todo.model_dump()  # подготовка данных для внесения в БД
        async with self.uow:  # вход в контекст (если выбьет с ошибкой, то изменения откатятся)
            todo_from_db = await self.uow.todo.add_one(todo_dict)
            todo_to_return = ToDoFromDB.model_validate(
                todo_from_db
            )  # обработка полученных данных из БД для их возврата - делаем модель пидантик
            await self.uow.commit()  # это самый важный кусок кода, до этого коммита можно записать данные в 50 моделей, но если кто-то вылетит с ошибкой, все изменения откатятся! Если код дошёл сюда, то все прошло окей!
            return todo_to_return

    async def get_todos(self) -> list[ToDoFromDB]:
        async with self.uow:
            todos: list = await self.uow.todo.find_all()
            return [ToDoFromDB.model_validate(todo) for todo in todos]
