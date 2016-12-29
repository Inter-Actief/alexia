from django.forms import BaseInlineFormSet


class EmptyInlineFormSet(BaseInlineFormSet):
    def __iter__(self):
        """Yield all forms plus an empty (template) form"""
        for form in self.forms:
            yield form
        yield self.empty_form

    def __len__(self):
        return len(self.forms) + 1
