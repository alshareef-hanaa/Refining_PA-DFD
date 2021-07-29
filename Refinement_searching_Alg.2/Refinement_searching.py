import sys
import xml.etree.ElementTree as ET
import csv


# First step function for producing B-DFD (typed) in csv format from XML
def initialize(xmlfile_DFD, csvfile_DFD):
    tree = ET.parse(xmlfile_DFD)
    root = tree.getroot()
    newsitems = []

    for subroot in root:
        for subsubroot in subroot:
            for subsubsubroot in subsubroot:
                for child in subsubsubroot:
                    news = {}
                    if int(child.attrib['id']) >= 2:
                        news['id'] = int(child.attrib['id'])
                        news['value'] = child.attrib['value']
                        if child.attrib['style'].startswith("rounded=0"):
                            news['style'] = 'rounded=0'
                            news['source'] = 'null'
                            news['target'] = 'null'
                            news['type'] = 'external_entity'
                        elif "doubleEllipse" in child.attrib['style']:
                            news['style'] = 'ellipse;shape=doubleEllipse'
                            news['source'] = 'null'
                            news['target'] = 'null'
                            news['type'] = 'composite_process'
                        elif child.attrib['style'].startswith("ellipse"):
                            news['style'] = 'ellipse'
                            news['source'] = 'null'
                            news['target'] = 'null'
                            news['type'] = 'process'
                        elif child.attrib['style'].startswith("shape"):
                            news['style'] = 'shape=partialRectangle'
                            news['source'] = 'null'
                            news['target'] = 'null'
                            news['type'] = 'data_base'
                        elif child.attrib['style'].startswith("endArrow=classic"):
                            news['source'] = child.attrib['source']
                            news['target'] = child.attrib['target']
                            news['style'] = 'endArrow=classic'
                            news['type'] = 'endArrow=classic'
                        elif child.attrib['style'].startswith("endArrow=cross"):
                            news['source'] = child.attrib['source']
                            news['target'] = child.attrib['target']
                            news['style'] = 'endArrow=cross'
                            news['type'] = 'endArrow=cross'
                        newsitems.append(news)

    fields = ['id', 'value', 'style', 'source', 'target', 'type']
    with open(csvfile_DFD, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(newsitems)


# this function changes the format of DFD from csv to dic
def generate_dic_dfd(filename):
    data = csv.DictReader(open(filename))
    data_dic = []
    for row in data:
        data_dic.append(row)
    return data_dic


# this function changes the format of DFD from dic to nested dic
# where key is the id of each DFD element (activators and flows)
def generate_dfd_graph(original):
    output = {}
    for elem in original:
        output[elem['id']] = elem
    return output


# this function assigns type to each flow in DFD (that format as nested dic)
def get_data_flow_types(dfd_graph):
    for index, data_flow in dfd_graph.items():
        if data_flow['style'] == 'endArrow=classic':
            if dfd_graph[data_flow['source']]['style'] == 'rounded=0' and dfd_graph[data_flow['target']][
                'style'] == 'ellipse':
                dfd_graph[index]['type'] = 'in'
            if dfd_graph[data_flow['source']]['style'] == 'rounded=0' and dfd_graph[data_flow['target']][
                'style'] == 'ellipse;shape=doubleEllipse':
                dfd_graph[index]['type'] = 'inc'
            elif dfd_graph[data_flow['source']]['style'] == 'ellipse' and dfd_graph[data_flow['target']][
                'style'] == 'rounded=0':
                dfd_graph[index]['type'] = 'out'
            elif dfd_graph[data_flow['source']]['style'] == 'ellipse;shape=doubleEllipse' and \
                    dfd_graph[data_flow['target']]['style'] == 'rounded=0':
                dfd_graph[index]['type'] = 'outc'
            elif (dfd_graph[data_flow['source']]['style'] == 'ellipse' and dfd_graph[data_flow['target']][
                'style'] == 'ellipse'):
                dfd_graph[index]['type'] = 'comp'
            elif (dfd_graph[data_flow['source']]['style'] == 'ellipse;shape=doubleEllipse' and
                  dfd_graph[data_flow['target']]['style'] == 'ellipse;shape=doubleEllipse'):
                dfd_graph[index]['type'] = 'ccompc'
            elif (dfd_graph[data_flow['source']]['style'] == 'ellipse;shape=doubleEllipse' and
                  dfd_graph[data_flow['target']]['style'] == 'ellipse'):
                dfd_graph[index]['type'] = 'ccomp'
            elif (dfd_graph[data_flow['source']]['style'] == 'ellipse' and
                  dfd_graph[data_flow['target']]['style'] == 'ellipse;shape=doubleEllipse'):
                dfd_graph[index]['type'] = 'compc'
            elif dfd_graph[data_flow['source']]['style'] == 'ellipse' and dfd_graph[data_flow['target']][
                'style'] == 'shape=partialRectangle':
                dfd_graph[index]['type'] = 'store'
            elif dfd_graph[data_flow['source']]['style'] == 'ellipse;shape=doubleEllipse' and \
                    dfd_graph[data_flow['target']][
                        'style'] == 'shape=partialRectangle':
                dfd_graph[index]['type'] = 'cstore'
            elif dfd_graph[data_flow['source']]['style'] == 'shape=partialRectangle' and dfd_graph[data_flow['target']][
                'style'] == 'ellipse':
                dfd_graph[index]['type'] = 'read'
            elif dfd_graph[data_flow['source']]['style'] == 'shape=partialRectangle' and dfd_graph[data_flow['target']][
                'style'] == 'ellipse;shape=doubleEllipse':
                dfd_graph[index]['type'] = 'cread'
            if data_flow['style'] == 'endArrow=cross':
                if dfd_graph[data_flow['source']]['style'] == 'ellipse' and dfd_graph[data_flow['target']][
                    'style'] == 'shape=partialRectangle':
                    dfd_graph[index]['type'] = 'delete'
                elif dfd_graph[data_flow['source']]['style'] == 'ellipse;shape=doubleEllipse' and \
                        dfd_graph[data_flow['target']]['style'] == 'shape=partialRectangle':
                    dfd_graph[index]['type'] = 'cdelete'
    return dfd_graph


# function for create nodes, edges, sources, targets, type, labels dictionaries for each DFD dic
def generate_dfd_as_dics(typed_dfd_nested_dic):
    nodes_dic = set()
    edges_dic = set()
    types_dic = dict()
    labels_dic = dict()
    sources_dic = dict()
    targets_dic = dict()
    node_types = ['external_entity', 'composite_process', 'process', 'data_base']
    for index, element in typed_dfd_nested_dic.items():
        if element['type'] in node_types:
            nodes_dic.add(element['id'])
            new = {element['id']: element['type']}
            types_dic.update(new)
            new = {element['id']: element['value']}
            labels_dic.update(new)
        else:
            edges_dic.add(element['id'])
            new = {element['id']: element['type']}
            types_dic.update(new)
            new = {element['id']: element['value']}
            labels_dic.update(new)
            new = {element['id']: element['source']}
            sources_dic.update(new)
            new = {element['id']: element['target']}
            targets_dic.update(new)
    return nodes_dic, edges_dic, sources_dic, targets_dic, types_dic, labels_dic


def has_dom(f, a):
    dom_f = set(f.keys())
    return dom_f.issubset(a)


def has_cod(f, b):
    cod_f = set(f.values())
    loop = 'O'
    if loop in cod_f:
        cod_f.remove('O')
    return cod_f.issubset(b)


# check that every nodes/edges has type and label

def has_type(nodes, edges, f_types):
    elements_types = set(f_types.keys())
    total_elements = len(nodes) + len(edges)
    return len(elements_types) == total_elements


def has_label(nodes, edges, f_labels):
    elements_labels = set(f_labels.keys())
    total_elements = len(nodes) + len(edges)
    return len(elements_labels) == total_elements


def is_total_map(f, a):
    dom_f = set(f.keys())
    return dom_f == a


def is_surjective_map(f, b):
    cod_f = set(f.values())
    return cod_f == b


def is_injective_map(f, a):
    for x in a:
        fx = f[x]
        for y in a:
            fy = f[y]
            if (x != y) and (fx == fy): return False
    return True


def is_correct_type(f):
    system_types = (
        'composite_process', 'data_base', 'external_entity', 'process', 'compc', 'ccomp', 'cread', 'cstore', 'read',
        'store', 'comp', 'delete', 'in', 'out', 'cdelete', 'inc', 'outc')
    elements_types = set(f.values())
    return elements_types.issubset(system_types)


class Graph:
    def __init__(self, nodes, edges, src, tgt, elements_types, elements_labels):

        # Check that the source and target maps are total.
        if not is_total_map(src, edges):
            raise ValueError("source map not total!")
        if not is_total_map(tgt, edges):
            raise ValueError("target map not total!")
        if not has_cod(src, nodes):
            raise ValueError("source map has non-node values!")
        if not has_cod(tgt, nodes):
            raise ValueError("target map has non-node values!")
        if not has_type(nodes, edges, elements_types):
            raise ValueError("node/edge is non-typed!")
        if not has_label(nodes, edges, elements_labels):
            raise ValueError("node/edge has no label !")
        if not is_correct_type(elements_types):
            raise ValueError("element(s) has type outside of type taxonomy")

        self.nodes = nodes
        self.edges = edges
        self.src = src
        self.tgt = tgt
        self.elements_types = elements_types
        self.elements_labels = elements_labels

    # For printing

    def __repr__(self):
        return ("Graph(" + repr(self.nodes) + ", " + repr(self.edges) + ", " +
                repr(self.src) + ", " + repr(self.tgt) + ", " + repr(self.elements_types) + ", " + repr(
                    self.elements_labels) + ")")

    # For comparisons

    def __eq__(self, other):
        return (self.nodes == other.nodes and self.edges == other.edges and
                self.src == other.src and self.tgt == other.tgt)

    def __neq__(self, other):
        return not __eq__(self, other)


# Check types according the taxonomy of node types and edge types of our framework
def check_type(x_type, y_type):
    ccompc_subtypes = {'ccompc', 'compc', 'ccomp', 'cread', 'cstore', 'read', 'store', 'comp'}
    compc_subtypes = {'compc', 'read', 'comp', 'store'}
    ccomp_subtypes = {'ccomp', 'store', 'read', 'comp'}
    cread_subtypes = {'cread', 'read'}
    cstore_subtypes = {'cstore', 'store'}
    cdelete_subtypes = {'cdelete', 'delete'}
    inc_subtypes = {'inc', 'in'}
    outc_subtypes = {'outc', 'out'}
    cproc_subtypes = {'composite_process', 'process', 'data_base'}

    if y_type == 'ccompc':
        if x_type in ccompc_subtypes:
            return True
        else:
            return False
    elif y_type == 'compc':
        if x_type in compc_subtypes:
            return True
        else:
            return False
    elif y_type == 'ccomp':
        if x_type in ccomp_subtypes:
            return True
        else:
            return False
    elif y_type == 'cread':
        if x_type in cread_subtypes:
            return True
        else:
            return False
    elif y_type == 'cstore':
        if x_type in cstore_subtypes:
            return True
        else:
            return False
    elif y_type == 'cdelete':
        if x_type in cdelete_subtypes:
            return True
        else:
            return False
    elif y_type == 'inc':
        if x_type in inc_subtypes:
            return True
        else:
            return False
    elif y_type == 'outc':
        if x_type in outc_subtypes:
            return True
        else:
            return False
    elif y_type == 'composite_process':
        if x_type in cproc_subtypes:
            return True
        else:
            return False
    elif y_type == 'external_entity':
        if x_type == 'external_entity':
            return True
        else:
            return False
    elif y_type == 'data_base':
        if x_type == 'data_base':
            return True
        else:
            return False
    elif y_type == 'process':
        if x_type == 'process':
            return True
        else:
            return False
    elif y_type == 'in':
        if x_type == 'in':
            return True
        else:
            return False
    elif y_type == 'out':
        if x_type == 'out':
            return True
        else:
            return False
    elif y_type == 'comp':
        if x_type == 'comp':
            return True
        else:
            return False
    elif y_type == 'store':
        if x_type == 'store':
            return True
        else:
            return False
    elif y_type == 'read':
        if x_type == 'read':
            return True
        else:
            return False


class Hom:
    def __init__(self, dom, cod, node_map, edge_map):

        # Check that the node and edge maps have the right domains and
        # codomains.

        if not has_dom(node_map, dom.nodes):
            raise ValueError("node map has key outside dom.nodes!")
        if not has_dom(edge_map, dom.edges):
            raise ValueError("edge map has key outside dom.edges!")
        if not has_cod(node_map, cod.nodes):
            raise ValueError("node map has value outside cod.nodes!")
        if not has_cod(edge_map, cod.edges):
            raise ValueError("edge map has value outside cod.edges!")

        # Graph homomorphisms must preserve sources and targets.
        for e, e_value in edge_map.items():
            e_src = dom.src[e]
            e_tgt = dom.tgt[e]
            if e_value == 'O':
                if node_map[e_src] != node_map[e_tgt] or cod.elements_types[node_map[e_src]] != 'composite_process':
                    raise ValueError("mapping of internal flow is not internal")
            else:
                fe_src = cod.src[e_value]
                fe_tgt = cod.tgt[e_value]
                if node_map[e_src] != fe_src:
                    raise ValueError("does not preserve sources")
                if node_map[e_tgt] != fe_tgt:
                    raise ValueError("does not preserve targets")
                if not check_type(dom.elements_types[e], cod.elements_types[e_value]):
                    raise ValueError("mapping flows does not preserve types")
                if not check_type(dom.elements_types[e_src], cod.elements_types[fe_src]):
                    raise ValueError("mapping nodes does not preserve types")
                if not check_type(dom.elements_types[e_tgt], cod.elements_types[fe_tgt]):
                    raise ValueError("mapping nodes does not preserve types")

        self.dom = dom
        self.cod = cod
        self.node_map = node_map
        self.edge_map = edge_map

    def is_total(self):
        return (is_total_map(self.node_map, self.dom.nodes) and
                is_total_map(self.edge_map, self.dom.edges))

    def is_surjective(self):
        return (is_surjective_map(self.node_map, self.cod.nodes) and
                is_surjective_map(self.edge_map, self.cod.edges))

    def is_injective(self):
        return (is_injective_map(self.node_map, self.dom.nodes) and
                is_injective_map(self.edge_map, self.dom.edges))

        # Return a new Hom with extended node and edge mappings.

    def extended(self, node_ext, edge_ext):
        new_node_map = self.node_map.copy()
        new_node_map.update(node_ext)
        new_edge_map = self.edge_map.copy()
        new_edge_map.update(edge_ext)
        # FIXME print("self =", self)
        # print(new_node_map)
        # print(new_edge_map)
        return Hom(self.dom, self.cod, new_node_map, new_edge_map)

        # For printing

    def __repr__(self):
        return ("Hom(" + repr(self.dom) + ", " + repr(self.cod) + ", " +
                repr(self.node_map) + ", " + repr(self.edge_map) + ")")

        # For comparisons

    def __eq__(self, other):
        return (self.dom == other.dom and self.cod == other.cod and
                self.node_map == other.node_map and
                self.edge_map == other.edge_map)

    def __neq__(self, other):
        return not __eq__(self, other)


def extend_to_hom(p):
    # A helper function that keeps track of the un-mapped edges
    # explicitly in an (immutable) list 'unmapped'.  In Python, an
    # immutable list is just a (nested) tuple.

    def ext(p, unmapped):
        if unmapped:  # is 'unmapped' non-empty?

            # 'unmapped' is non-empty, i.e. there remain unmapped
            # elements.  Pick the first element and try mapping it.
            #
            e, rest = unmapped
            assert (not e in p.edge_map)  # e is really unmapped
            e_src = p.dom.src[e]
            e_tgt = p.dom.tgt[e]
            e_label = p.dom.elements_labels[e]
            e_src_label = p.dom.elements_labels[e_src]
            e_tgt_label = p.dom.elements_labels[e_tgt]
            e_type = p.dom.elements_types[e]
            e_src_type = p.dom.elements_types[e_src]
            e_tgt_type = p.dom.elements_types[e_tgt]

            results = []
            # Iterate through all the nodes 'm' to find extension where e is internal
            for m in p.cod.nodes:
                n_ext = dict()
                # check if the candidate conflicts with existing mappings of e_src and e_tgt
                if (e_src in p.node_map and p.node_map[e_src] != m) or (e_tgt in p.node_map and p.node_map[e_tgt] != m):
                    continue
                # check types
                if (p.cod.elements_types[m] != 'composite_process') or (
                        not check_type(e_src_type, 'composite_process')) or (
                        not check_type(e_tgt_type, 'composite_process')):
                    continue
                if e_src not in p.node_map:
                    n_ext[e_src] = m
                if e_tgt not in p.node_map:
                    n_ext[e_tgt] = m
                p_ext = p.extended(n_ext, {e: 'O'})
                result = ext(p_ext, rest)
                results += result

            # Iterate through all the candiates 'c', i.e. all the
            # edges in the codomain graph, and check whether 'e' can
            # be mapped to 'c'.

            for c in p.cod.edges:
                c_src = p.cod.src[c]
                c_tgt = p.cod.tgt[c]
                c_label = p.cod.elements_labels[c]
                c_src_label = p.cod.elements_labels[c_src]
                c_tgt_label = p.cod.elements_labels[c_tgt]
                c_type = p.cod.elements_types[c]
                c_src_type = p.cod.elements_types[c_src]
                c_tgt_type = p.cod.elements_types[c_tgt]

                # Check if the source and target nodes of 'e' are
                # already mapped, and if so, whether the mapping
                # fulfills the homomorphism property.  If it doesn't,
                # then 'c' is a bad candidate and we can skip ahead to
                # the next candidate.  Otherwise, we add the candidate
                # to 'p' and continue extending 'p' recursively.

                n_ext = dict()
                # check label
                if c_label != e_label:
                    continue

                # check if the candidate conflicts with existing mappings of e_src and e_tgt
                if (e_src in p.node_map and p.node_map[e_src] != c_src) or (
                        e_tgt in p.node_map and p.node_map[e_tgt] != c_tgt):
                    continue

                # check types
                if (not check_type(e_type, c_type)) or (not check_type(e_src_type, c_src_type)) or (
                        not check_type(e_tgt_type, c_tgt_type)):
                    continue

                # check nodes (source and target) labels:
                # check source label
                # in case of ext, db and proc labels should be matched
                if e_src_type == c_src_type and e_src_label != c_src_label and e_src_type != 'composite_process':
                    continue
                # in case of cproc
                if e_src_type == 'composite_process' and c_src_type == 'composite_process':
                    if e_src_label != c_src_label:
                        if any((p.cod.elements_labels[item] == e_src_label) and (
                                p.cod.elements_types[item] == e_src_type) for item in p.cod.nodes):
                            continue

                if e_src not in p.node_map:
                    n_ext[e_src] = c_src

                # check target label
                # in case of ext, db and proc labels should be matched
                if e_tgt_type == c_tgt_type and e_tgt_label != c_tgt_label and e_tgt_type != 'composite_process':
                    continue
                # in case of cproc
                if e_tgt_type == 'composite_process' and c_tgt_type == 'composite_process':
                    if e_tgt_label != c_tgt_label:
                        if any((p.cod.elements_labels[item] == e_tgt_label) and (
                                p.cod.elements_types[item] == e_tgt_type) for item in p.cod.nodes):
                            continue
                if e_tgt not in p.node_map:
                    n_ext[e_tgt] = c_tgt

                p_ext = p.extended(n_ext, {e: c})
                result = ext(p_ext, rest)
                results += result
            return results
        else:  # 'unmapped' is empty, so 'p' is already total.
            assert p.is_total()
            return [p]

    # Turn a collection into a nested tuple (aka an immutable list).
    def nested_tuple(col):
        t = ()
        for x in col:
            t = (x, t)
        return t

    # Compute the set of unmapped edges and turn it into a nested
    # tuple.
    mapped_edges = p.edge_map.keys()
    unmapped_edges = p.dom.edges.difference(mapped_edges)
    unmapped_as_tuple = nested_tuple(unmapped_edges)
    return ext(p, unmapped_as_tuple)


# Find all the graph homomorphisms between 'g' and 'h'.

def find_homs(g, h, node_map, edge_map):
    empty_hom = Hom(g, h, node_map, edge_map)
    return extend_to_hom(empty_hom)


# For readability
def print_homs(a, b, fs):
    def tgt_lbl(labels, n):
        if n == 'O':
            return '(loop)'
        else:
            return labels[n]

    print("homs from", a, "to", b, ":")
    i = 0
    for f in fs:
        gl = f.dom.elements_labels
        hl = f.cod.elements_labels
        print("hom #" + str(i) + ":")
        print("  node map:")
        for k, v in f.node_map.items():
            print("   ", gl[k], "->", tgt_lbl(hl, v))
        print("  edge map:")
        for k, v in f.edge_map.items():
            print("   ", gl[k], "->", tgt_lbl(hl, v))
        i += 1


def find_surjective_homs(g, h, node_map, edge_map):
    homs = find_homs(g, h, node_map, edge_map)
    return [f for f in homs if f.is_surjective()]


# set the four files
dfd_a_xml_filename = sys.argv[1]
dfd_a_csv_filename = sys.argv[2]
dfd_c_xml_filename = sys.argv[3]
dfd_c_csv_filename = sys.argv[4]
nodes_abstraction = sys.argv[5]
edges_abstraction = sys.argv[6]
balanced_options = sys.argv[7]

# B-DFD abstract level
initialize(dfd_a_xml_filename, dfd_a_csv_filename)
dfd_a_dic = generate_dic_dfd(dfd_a_csv_filename)
dfd_a_nested_dic = generate_dfd_graph(dfd_a_dic)
typed_dfd_a_nested_dic = get_data_flow_types(dfd_a_nested_dic)
nodes_a_dic, edges_a_dic, sources_a_dic, targets_a_dic, types_a_dic, labels_a_dic = generate_dfd_as_dics(
    typed_dfd_a_nested_dic)
dfd_a_graph = Graph(nodes_a_dic, edges_a_dic, sources_a_dic, targets_a_dic, types_a_dic, labels_a_dic)

# B-DFD concrete level
initialize(dfd_c_xml_filename, dfd_c_csv_filename)
dfd_c_dic = generate_dic_dfd(dfd_c_csv_filename)
dfd_c_nested_dic = generate_dfd_graph(dfd_c_dic)
typed_dfd_c_nested_dic = get_data_flow_types(dfd_c_nested_dic)
nodes_c_dic, edges_c_dic, sources_c_dic, targets_c_dic, types_c_dic, labels_c_dic = generate_dfd_as_dics(
    typed_dfd_c_nested_dic)
dfd_c_graph = Graph(nodes_c_dic, edges_c_dic, sources_c_dic, targets_c_dic, types_c_dic, labels_c_dic)


def generate_mapping_info(abstraction_csv_filename):
    with open(abstraction_csv_filename) as csv_file:
        abstraction = csv.DictReader(csv_file)
        abstraction_list = [row for row in abstraction]
        abstraction_info = dict()
        # generate abstraction info
        for c_id in abstraction_list:
            abstraction_info[c_id['id']] = abstraction_info[c_id['map_to']]
    return abstraction_info


nodes_abstraction_dic = generate_mapping_info(nodes_abstraction)
edges_abstraction_dic = generate_mapping_info(edges_abstraction)

abstractions_result = []
if balanced_options == 'balanced':
    abstractions_result = find_surjective_homs(dfd_c_graph, dfd_a_graph, nodes_abstraction_dic, edges_abstraction_dic)
elif balanced_options == 'all':
    abstractions_result = find_homs(dfd_c_graph, dfd_a_graph, nodes_abstraction_dic, edges_abstraction_dic)

print_homs("Concrete B-DFD", "Abstraction B-DFD", abstractions_result)
