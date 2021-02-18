from subprocess import Popen, PIPE
import os

def evaluate(image_path):
    # test dd
    if not os.path.isdir('dd_pretrained'):
        return []

    p = Popen(['deepdanbooru', 'evaluate', image_path, '--project-path', 'dd_pretrained', '--allow-folder'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")

    # remove first and last lines which are not tags
    lines = str(output).split('\\n')[1:-3]
    tags = [line.split()[1] for line in lines]
    return tags

def union(tags=None, dd_tags=None):
    '''
    Return a string of tags which include the normal ones and dd
    '''
    tag_set = set(tags.split())
    dd_tags = list( tag_set.union(set(dd_tags)) )
    dd_tags = '|{}|'.format('|'.join(dd_tags))

    return dd_tags
