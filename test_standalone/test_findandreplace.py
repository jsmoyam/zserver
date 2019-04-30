import subprocess, os

def escape_string(text):
    # Replace slash for backslash and slash
    text_escape = ''
    for c in text:
        new_c = c
        if c == '/':
            new_c = '\/'
        text_escape = text_escape + new_c
    return text_escape

def find_replace(path, text, replacement):
    # grep - rl "/pepe/juan" * | xargs sed - i 's/\/tmp\/venv/\/home\/tmp/g'

    text_escape = escape_string(text)
    replacement_escape = escape_string(replacement)
    command = 'grep -rl "{}" {}'.format(text, path) + os.sep + '* | xargs sed -i "s/{}/{}/g"'.format(text_escape, replacement_escape)
    os.system(command)



# find_replace('/tmp/venv/bin', '/tmp/venv', '/pepe/juan')

a = subprocess.check_output('whereis chmod', shell=True)
print(a)