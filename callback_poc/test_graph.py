from graph import Workflow, Execution, Task
import pytest


@pytest.fixture
def example_workflow():
    w = Workflow(name="test_workflow")
    root = w.add_task(name="root")
    two = w.add_task(name="two", dependencies=[root])
    three = w.add_task(name="three", dependencies=[root])
    four = w.add_task(name="four", dependencies=[root])
    five = w.add_task(name="five", dependencies=[two])
    six = w.add_task(name="six", dependencies=[two, three])
    seven = w.add_task(name="seven", dependencies=[two, three])
    eight = w.add_task(name="eight", dependencies=[four])
    nine = w.add_task(name="nine", dependencies=[four])
    ten = w.add_task(name="ten", dependencies=[five, eight, nine])

    return w


def test_get_execution_tree(example_workflow):
    w = example_workflow
    expected = {
        frozenset(): {w.tasks["root"]},
        frozenset({w.tasks["root"]}): {
            w.tasks["three"],
            w.tasks["two"],
            w.tasks["four"],
        },
        frozenset({w.tasks["two"]}): {w.tasks["five"]},
        frozenset({w.tasks["three"], w.tasks["two"]}): {
            w.tasks["six"],
            w.tasks["seven"],
        },
        frozenset({w.tasks["four"]}): {w.tasks["eight"], w.tasks["nine"]},
        frozenset({w.tasks["five"], w.tasks["eight"], w.tasks["nine"]}): {
            w.tasks["ten"]
        },
    }
    assert expected == w.get_execution_tree()


def test_execution(example_workflow):
    w = example_workflow
    e = Execution(w)

    runnable = e.get_runnable()
    assert set(["root"]) == set([t.name for t in runnable])

    e.schedule_runnable()
    runnable = e.get_runnable()
    assert set(["four", "three", "two"]) == set([t.name for t in runnable])



# if __name__ == "__main__":
#     test_get_execution_tree()