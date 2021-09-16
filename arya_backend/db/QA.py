from typing import Optional, Union

from bson import ObjectId

# from pymongo.client_session import ClientSession
from pymongo.collation import Collation

from arya_backend.db import MONGO_DB_NAME, client
from arya_backend.models.qa import QA, DragAnswer, JoinAnswer, ManyAnswer, OneAnswer

QA_COLLECTION_NAME = "QA"

collection = client.get_database(MONGO_DB_NAME).get_collection(QA_COLLECTION_NAME)


collection.create_index("question", collation=Collation(locale="ru", strength=2))


class QACRUD:
    def get(self, id: ObjectId) -> Optional[QA]:
        doc = collection.find_one({"_id": id})
        if doc:
            return QA.parse_obj(doc)

    def add_result(
        self,
        id: ObjectId,
        answer: Union[OneAnswer, ManyAnswer, JoinAnswer, DragAnswer],
        is_correct: bool,
    ):

        if is_correct is True:
            collection.update_one({"_id": id}, {"$set": {"correct": answer.to_mongo()}})
        elif is_correct is False:
            qa = QA.parse_obj(collection.find_one({"_id": id}))
            incorect = set(qa.incorrect)
            incorect.add(answer)  # type: ignore
            incorect = list([el.to_mongo() for el in incorect])  # type: ignore
            collection.update_one({"_id": id}, {"$set": {"incorrect": incorect}})

    def load_or_create_complete_qa(self, qa: QA):
        if qa.incomplete:
            ValueError("qa must be complete")
        filter = {
            "question": qa.question,
            "type": qa.type,
            "incomplete": qa.incomplete,
            "$expr": {"$setEquals": [qa.answers, "$answers"]},
        }
        doc = collection.find_one(filter=filter)
        if doc:
            return QA.parse_obj(doc)
        else:
            _id = collection.insert_one(qa.to_mongo()).inserted_id
            return qa.copy(update={"id": _id})

    def get_or_create(self, qa: QA):
        pipeline = [
            {
                "$match": {
                    "$and": [
                        {"question": qa.question},
                        {"type": qa.type},
                        {
                            "$or": [
                                {
                                    "incomplete": True,
                                    "$expr": {"$setIsSubset": [qa.answers, "$answers"]},
                                },
                                {
                                    "incomplete": False,
                                    "$expr": {"$setEquals": [qa.answers, "$answers"]},
                                },
                            ]
                        },
                    ]
                }
            }
        ]
        for row_qa in collection.aggregate(pipeline):
            qa_in_db = QA.parse_obj(row_qa)
            if qa_in_db.incomplete is False:
                if qa_in_db.correct == qa.correct:
                    if qa.incorrect.issubset(qa_in_db.incorrect):
                        return ("exist", qa_in_db.id)
                    else:
                        collection.update_one(
                            {"_id": qa_in_db.id},
                            {"incorrect": qa.incorrect.union(qa_in_db.incorrect)},
                        )
                        return ("update", qa_in_db.id)
                else:
                    id = collection.insert_one(qa.to_mongo()).inserted_id
                    return ("new", id)
            if qa_in_db.incomplete is True and qa.incomplete is False:
                id = collection.insert_one(qa.to_mongo()).inserted_id
                return ("new", id)
            if qa_in_db.incomplete is True and qa.incomplete is True:
                if (
                    qa_in_db.correct == qa.correct
                    and qa_in_db.incorrect == qa.incorrect
                ):
                    return ("exist", qa_in_db.id)
                else:
                    id = collection.insert_one(qa.to_mongo()).inserted_id
                    return ("new", id)
        else:
            id = collection.insert_one(qa.to_mongo()).inserted_id
            return ("new", id)


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
