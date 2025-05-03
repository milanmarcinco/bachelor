from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert import Indexer

from lib.conf import EXPERIMENT, ROOT_PATH, CHECKPOINT_PATH, MODEL_NAME, UNITS
from lib.helpers import now

if __name__ == '__main__':
    for unit in UNITS:
        print(now(), "Indexing started")
        
        with Run().context(RunConfig(nranks=1, experiment=EXPERIMENT)):
            config = ColBERTConfig(
                nbits=2,
                root=ROOT_PATH,
                model_name=MODEL_NAME
            )

            indexer = Indexer(checkpoint=CHECKPOINT_PATH, config=config)

            index_name = f"{unit}_index"
            collection_path = f"{ROOT_PATH}/{unit}s_collection.tsv"

            indexer.index(
                name=index_name,
                collection=collection_path,
                overwrite=True
            )

        print(now(), "Indexing finished")
