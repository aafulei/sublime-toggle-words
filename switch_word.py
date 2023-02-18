# sublime
import sublime
import sublime_plugin

NAME = "Switch Word"

g_word_lists = [["true", "false"],
                  ["True", "False"],
                  ["TRUE", "FALSE"]]

g_set_filename = "switch-word.sublime-settings"


# false
# FALSE
# False
# Blue
# Blue
# BLUE


def plugin_loaded():
    _load_settings()


def _log_error(*args):
    print("[{}] Error:".format(NAME), *args)


def _log_info(*args):
    print("[{}] Info:".format(NAME), *args)


def _check_word_lists(word_lists):
    if not isinstance(word_lists, list):
        _log_error("word_lists not a list")
        return False
    for lst in word_lists:
        if not isinstance(lst, list):
            _log_error("word_lists not a list of lists")
            return False
        if len(lst) < 2:
            _log_error("length-{} list found in word_lists".format(len(lst)))
            return False
        for word in lst:
            if not isinstance(word, str):
                _log_error("non-str element found in word_lists")
                return False
        if len(lst) != len(set(lst)):
            _log_error("duplicates found in word_lists")
            return False
    return True


def _load_settings():
    global g_word_lists
    settings = sublime.load_settings(g_set_filename)
    if not settings.has("word_lists"):
        _log_error("word_lists not found in {}, will use default".format(g_set_filename))
    elif not _check_word_lists(settings.get("word_lists")):
        _log_error("invalid word_lists, will use default")
    else:
        g_word_lists = settings.get("word_lists")
    _log_info("loaded word lists:", g_word_lists)


def get_word_to_swap_with(word):
    for i, lst in enumerate(g_word_lists):
        for j, target in enumerate(lst):
            if word == target:
                new_word = lst[(j + 1) % len(lst)]
                return new_word
    return ""


class SwitchWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        old_sel = list(self.view.sel())
        to_expand = []
        to_modify = []
        for region in old_sel:
            if region.empty():
                to_expand.append(region.begin())
            else:
                word = self.view.substr(region)
                new_word = get_word_to_swap_with(word)
                if new_word:
                    b = region.begin()
                    e = region.end()
                    to_modify.append((b, e, new_word))

        for point in to_expand:
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(point, point))
            self.view.run_command("expand_selection", {"to": "word"})
            region = self.view.sel()[0]
            word = self.view.substr(region)
            new_word = get_word_to_swap_with(word)
            if new_word:
                b = region.begin()
                e = region.end()
                to_modify.append((b, e, new_word))

        self.view.sel().clear()
        self.view.sel().add_all(old_sel)

        to_modify = sorted(list(set(to_modify)))

        # print(to_expand)
        # print(to_modify)

        offset = 0
        for b, e, w in to_modify:
            reg = sublime.Region(b + offset, e + offset)
            self.view.replace(edit, reg, w)
            offset += len(w) - (e - b)

        return
