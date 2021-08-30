from typing import Optional

from bson import ObjectId

# from pymongo.client_session import ClientSession
from pymongo.collation import Collation

from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.qa import QA, JoinAnswer, ManyAnswer, OneAnswer

QA_COLLECTION_NAME = "QA"

collection = client.get_database(MONGO_DB_NAME).get_collection(QA_COLLECTION_NAME)


collection.create_index("question", collation=Collation(locale="ru", strength=2))


class QACRUD:
    def get(self, id: ObjectId) -> Optional[QA]:
        doc = collection.find_one({"_id": id})
        if doc:
            return QA.parse_obj(doc)

    def get_or_create(self, qa: QA):
        if qa.incomplete:
            return self._get_or_create_incomplete_qa(qa)
        else:
            return self._get_or_create_complete_qa(qa)

    def _get_or_create_complete_qa(self, qa: QA):
        ...

    def _get_or_create_incomplete_qa(self, qa: QA):
        filter = {
            "type": qa.type,
            "question": qa.question,
            "answers": {"$all": [{"$elemMatch": {"$eq": el}} for el in qa.answers]},
            "incomplete": qa.incomplete,
            "extra_answers": qa.extra_answers,
            **QACRUD._make_correct_query(qa),
        }
        update = {
            "$setOnInsert": {
                "incorrect": qa.incorrect,
                "tags": qa.tags,
                "answers": qa.answers,
            }
        }
        result = collection.update_one(filter=filter, update=update, upsert=True)
        if result.upserted_id is not None:
            return result.upserted_id, True
        result = list(collection.find(filter=filter))

    @staticmethod
    def _make_correct_query(qa: QA) -> dict:
        if qa.type == QA.type_enum.one and isinstance(qa.correct, OneAnswer):
            return {"correct": str(qa.correct)}
        elif qa.type == QA.type_enum.drag and isinstance(qa.correct, ManyAnswer):
            return {"correct": list(qa.correct)}
        elif qa.type == QA.type_enum.many and isinstance(qa.correct, ManyAnswer):
            return {
                "correct": {"$all": [{"$elemMatch": {"$eq": el}} for el in qa.correct]}
            }
        elif qa.type == QA.type_enum.join and isinstance(qa.correct, JoinAnswer):
            return {f"correct.{key}": value for key, value in qa.correct.items()}
        raise ValueError


# def is_exists(type: str, answer: list[str], question: str):
#     filter = {
#         "type": type,
#         "question": question,
#     }
#     if len(answer) == 1:
#         filter.update({"correct": answer[0]})
#     else:
#         filter.update(  # type: ignore
#             {
#                 "correct": {"$all": [{"$elemMatch": {"$eq": el}} for el in answer]},
#             }
#         )
#     qa = collection.find_one(filter=filter)
#     if qa:
#         return qa["_id"]


# def get_or_create_qa_incomplite(qa: QAIncomplete) -> Foreign:
#     def callback(session: ClientSession, qa: QAIncomplete):
#         col: Collection = session.client.get_database(MONGO_DB_NAME).get_collection(
#             "QA_INC"
#         )
#         filter = {
#             "question": qa.question,
#             "type": qa.type,
#             "title": qa.title,
#             "is_correct": qa.is_correct,
#             "answer": {"$all": [{"$elemMatch": {"$eq": el}} for el in qa.answer]},
#         }
#         doc = col.find_one(filter)
#         if doc is None:
#             doc = col.insert_one(qa.dict(exclude_none=True)).inserted_id
#             return Foreign(id=doc, col="QA_INC", new=True)
#         doc = col.find_one_and_update(
#             filter={"_id": doc["_id"]},
#             update={
#                 "$addToSet": {"by": qa.by[0]},
#             },
#         )
#         return Foreign(id=doc["_id"], col="QA_INC")

#     with client.start_session() as session:
#         return session.with_transaction(lambda s: callback(s, qa))


# def searc_inc(q: str):
#     pipeline = [
#         {
#             "$match": {
#                 "correct": {"$exists": True},
#                 "question": {"$regex": f".*{q}.*", "$options": "i"},
#             }
#         }
#     ]
#     doc = list(collection.aggregate(pipeline=pipeline))
#     pipeline_inc = [
#         {
#             "$match": {
#                 "is_correct": True,
#                 "question": {"$regex": f".*{q}.*", "$options": "i"},
#             }
#         },
#         {
#             "$group": {
#                 "_id": {"type": "$type", "question": "$question", "title": "$title"},
#                 "answers": {
#                     "$addToSet": {
#                         "answer": "$answer",
#                         "is_correct": "$is_correct",
#                         "id": "$_id",
#                     }
#                 },
#             }
#         },
#         {
#             "$project": {
#                 "answers": 1,
#                 "type": "$_id.type",
#                 "question": "$_id.question",
#                 "title": "$_id.title",
#                 "_id": 0,
#             }
#         },
#     ]
#     docs_inc = list(collection_incomplete.aggregate(pipeline=pipeline_inc))
#     return [*parse_obj_as(list[QA], doc), *parse_obj_as(list[QAINC], docs_inc)]
