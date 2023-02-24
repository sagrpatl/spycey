from IPython.display import HTML, display
import ipywidgets as widgets
from engineering_notation import EngNumber
import graphviz
from .powertree import PowerDotOutput

#  In progress....experimnetal for now

def IPowerTree(inputDevice, name="", inWidget={}):
    tab = widgets.Tab()
    children = []
    for idx, State in enumerate(inputDevice):
        Tree = State()
        argss = {}
        for x, y in inWidget.items():
            argss[x] = y
        paramKeys = list(inWidget.keys())
        argss["State"] = widgets.fixed(State)
        # TODO: Change below code to seed default value
        # Build Args
        # for item in dir(State):
        #         if not item.startswith("_"):
        #             if item not in ['name', 'callback']:
        #                 if item in paramKeys:
        #                     val = getattr(State,item)
        #                     argss[item].value = val
                        
        def plot(**args):
            # Some hackery
            # Strip State
            parameterKeys = list(args.keys())
            parameterKeys.remove('State')
            stripState = dict((k, args[k]) for k  in parameterKeys)   
            Tree = args["State"](**stripState)
            out = widgets.Output()
            with out:
                graph = graphviz.Source(PowerDotOutput(Tree))
                display(HTML('<div>{}</div>'.format(graph.pipe(format='svg', encoding='utf-8'))))
            display(out)
        plot_out = widgets.interactive(plot, **argss)    
        children.append(plot_out)    
    tab.children = children
    [tab.set_title(i, state.name) for i, state in enumerate(inputDevice)]
    
    return tab