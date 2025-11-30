from nicegui import ui

# build subpage app with nested subpages

def root():
    ui.label('Root Page')


    # add links to subpages
    ui.link('Index', '/').classes('block mb-2')
    ui.link('Sub Page 1', '/sub1').classes('block mb-2')
    ui.link('Sub Page 2', '/sub2').classes('block mb-2')

    ui.sub_pages({
        '/': index,
        '/sub1': sub1,
        '/sub2': sub2,
    })


def index():
    ui.label('Index Page')

def sub1():
    ui.label('Sub Page 1')

def sub2():
    ui.label('Sub Page 2')

    def nested_sub2():
        ui.label('Nested Sub Page 2')

    def other_sub2():
        ui.label('Other Sub Page 2')

    ui.sub_pages({
        '/': other_sub2,
        '/nested': nested_sub2
    })

    # add links to subpages
    ui.link('Other Sub Page 2', '/sub2/').classes('block mb-2')
    ui.link('Nested Sub Page 2', '/sub2/nested').classes('block mb-2')

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(root, title='Sub Pages Demo', reload=True)