import name_generator


def test_get_name():
    name = name_generator.get_name()
    adj, noun = name.split('-')
    assert adj in name_generator.adjectives
    assert noun  in name_generator.nouns
