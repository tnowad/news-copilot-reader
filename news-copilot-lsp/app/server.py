from pygls.server import LanguageServer
from lsprotocol.types import (
    CompletionList,
    CompletionParams,
    TextDocumentContentChangeEvent,
    CompletionItem,
)


class MyLanguageServer(LanguageServer):
    def __init__(self):
        super().__init__(name="news-copilot-lsp", version="0.0.1")
        self._completion_items = ["item1", "item2", "item3"]

    def _provide_completion_items(self) -> CompletionList:
        completions = [CompletionItem(label=item) for item in self._completion_items]
        return CompletionList(is_incomplete=False, items=completions)

    def provide_completion(self, params: CompletionParams) -> CompletionList:
        return self._provide_completion_items()

    def text_document_did_change(self, params: TextDocumentContentChangeEvent):
        pass


if __name__ == "__main__":
    server = MyLanguageServer()
    server.start_tcp("127.0.0.1", 8080)
