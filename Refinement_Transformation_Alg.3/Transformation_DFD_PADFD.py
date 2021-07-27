import sys
import xml.etree.ElementTree as ET
import csv


# function for producing dfd in csv format
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
                        news['DFD_element_id'] = int(child.attrib['id'])
                        news['target_type'] = []
                        newsitems.append(news)

    fields = ['id', 'value', 'style', 'source', 'target', 'type', 'DFD_element_id', 'target_type']
    with open(csvfile_DFD, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(newsitems)


# this function changes the format of DFD from csv to dic
def generate_dfd_dic(filename):
    data = csv.DictReader(open(filename))
    data_dic = []
    for row in data:
        data_dic.append(row)
    return data_dic


# this function changes the format of DFD from dic to nested dic
# where key is the id of each DFD element (activators and flows)
def generate_dfd_nested_dic(original):
    output = {}
    for elem in original:
        output[elem['id']] = elem
    return output


# this function assigns type to each flow in DFD
def get_dfd_flow_types(dfd_graph):
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


# --------------- creating DFD with target info (types)----------------- #


# this function sets the "target types" for each entity and flows in DFD
def typed_dfd_with_target_types(typed_dfd):
    for index, data_flow in typed_dfd.items():
        if typed_dfd[index]['type'] == 'external_entity':
            typed_dfd[index]['target_type'] = ['external_entity']
        elif typed_dfd[index]['type'] == 'composite_process':
            typed_dfd[index]['target_type'] = ['composite_process']
        elif typed_dfd[index]['type'] == 'process':
            typed_dfd[index]['target_type'] = ['process', 'reason']
        elif typed_dfd[index]['type'] == 'data_base':
            typed_dfd[index]['target_type'] = ['data_base', 'pol_DB']
        elif typed_dfd[index]['type'] == 'in':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'extlim', 'extreq', 'reqlim',
                                               'limlog', 'logging', 'reqrea', 'limpro']
        elif typed_dfd[index]['type'] == 'inc':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'extlim', 'extreq', 'reqlim',
                                               'limlog', 'logging', 'reqcpro', 'limcpro']
        elif typed_dfd[index]['type'] == 'out':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limext', 'reqext', 'reqlim',
                                               'limlog', 'logging', 'prolim', 'reareq']
        elif typed_dfd[index]['type'] == 'outc':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limext', 'reqext', 'reqlim',
                                               'limlog', 'logging', 'cprolim', 'cproreq']
        elif typed_dfd[index]['type'] == 'store':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limdb', 'reqpdb', 'reqlim',
                                               'limlog', 'logging', 'prolim', 'reareq', 'cledb_del', 'pdbcle']
        elif typed_dfd[index]['type'] == 'cstore':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limdb', 'reqpdb', 'reqlim',
                                               'limlog', 'logging', 'cprolim', 'cproreq', 'cledb_del', 'pdbcle']
        elif typed_dfd[index]['type'] == 'read':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limlog', 'logging', 'reqlim',
                                               'dblim', 'limpro', 'pdbreq', 'reqrea']
        elif typed_dfd[index]['type'] == 'cread':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limlog', 'logging', 'reqlim',
                                               'dblim', 'limcpro', 'pdbreq', 'reqcpro']
        elif typed_dfd[index]['type'] == 'delete':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limlog', 'logging', 'reqlim',
                                               'prolim', 'reareq', 'reqpdb', 'limdb_del']
        elif typed_dfd[index]['type'] == 'cdelete':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limlog', 'logging', 'reqlim',
                                               'cprolim', 'cproreq', 'reqpdb', 'limdb_del']
        elif typed_dfd[index]['type'] == 'comp':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limlog', 'logging', 'reqlim',
                                               'prolim', 'reareq', 'reqrea', 'limpro']
        elif typed_dfd[index]['type'] == 'ccomp':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limlog', 'logging', 'reqlim',
                                               'cprolim', 'cproreq', 'reqrea', 'limpro']
        elif typed_dfd[index]['type'] == 'compc':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limlog', 'logging', 'reqlim',
                                               'prolim', 'reareq', 'reqcpro', 'limcpro']
        elif typed_dfd[index]['type'] == 'ccompc':
            typed_dfd[index]['target_type'] = ['limit', 'request', 'log', 'DB_log', 'limlog', 'logging', 'reqlim',
                                               'cprolim', 'cproreq', 'reqcpro', 'limcpro']
    return typed_dfd


# TODO: this can be improved
def generate_dfd_csv_with_target_types(dfd_with_target_types, dfd_target_types_ids_csv_filename):
    csv_columns_1 = ['id', 'value', 'style', 'source', 'target', 'type', 'DFD_element_id', 'target_type']
    DFD_target_types = dfd_target_types_ids_csv_filename
    try:
        with open(DFD_target_types, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns_1)
            writer.writeheader()
            for key, data in dfd_with_target_types.items():
                writer.writerow(data)
    except IOError:
        print("I/O error")


# --------------- creating PADFD----------------- #

# this function add the common entities in transformation process
def add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements, limit_counter, request_counter, log_counter,
                               DB_log_counter, index):
    # add the new elements
    dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'limit %d' % limit_counter,
                                            'style': 'ellipse', 'source': 'null', 'target': 'null',
                                            'type': 'limit', 'DFD_element_id': index}
    len_of_dfd_elements = len_of_dfd_elements + 1
    dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'request %d' % request_counter,
                                            'style': 'ellipse', 'source': 'null', 'target': 'null',
                                            'type': 'request', 'DFD_element_id': index}
    len_of_dfd_elements = len_of_dfd_elements + 1
    dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'log %d' % log_counter,
                                            'style': 'ellipse', 'source': 'null', 'target': 'null',
                                            'type': 'log', 'DFD_element_id': index}
    len_of_dfd_elements = len_of_dfd_elements + 1
    dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'DB log %d' % DB_log_counter,
                                            'style': 'shape=partialRectangle', 'source': 'null',
                                            'target': 'null', 'type': 'DB_log', 'DFD_element_id': index}
    len_of_dfd_elements = len_of_dfd_elements + 1

    return dfd_graph_typed, len_of_dfd_elements


# this function applies PA-DFD transformation algorithm and produces PA-DFD nested dic
def generate_pa_dfd(dfd_graph_typed):
    len_of_dfd_elements = len(dfd_graph_typed) + 2

    # for transformation, we add new reason process for each process type
    reason_counter = 0
    for index, data_flow_typed in list(dfd_graph_typed.items()):
        if data_flow_typed['style'] == 'ellipse' and data_flow_typed['type'] == 'process':
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'reason %s' % data_flow_typed['value'],
                                                    'style': 'ellipse', 'source': 'null',
                                                    'target': 'null', 'type': 'reason',
                                                    'for_process': data_flow_typed['id'],
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1
            reason_counter = reason_counter + 1

    # for transformation, we add new policy data base for each type
    pol_DB_counter = 0
    for index, data_flow_typed in list(dfd_graph_typed.items()):
        if data_flow_typed['style'] == 'shape=partialRectangle' and data_flow_typed['type'] == 'data_base':
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'policy %d' % pol_DB_counter,
                                                    'style': 'shape=partialRectangle', 'source': 'null',
                                                    'target': 'null', 'type': 'pol_DB',
                                                    'for_DB': data_flow_typed['id'],
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1
            pol_DB_counter = pol_DB_counter + 1

    # to transform each type of data flows
    limit_counter = 0
    request_counter = 0
    log_counter = 0
    DB_log_counter = 0
    DB_pol_counter = 0
    clean_counter = 0

    # transfer all types of flow except comp
    for index, data_flow_typed in list(dfd_graph_typed.items()):

        # transform the 'in' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'in':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_in_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_in_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': data_flow_typed['value'],
                                                    'style': 'endArrow=classic', 'source': data_flow_typed['source'],
                                                    'target': target_in_limit, 'type': 'extlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            target_in_request = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_in_request = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'pol',
                                                    'style': 'endArrow=classic', 'source': data_flow_typed['source'],
                                                    'target': target_in_request, 'type': 'extreq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_in_log = None
            target_in_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_in_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_in_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_in_log,
                                                    'target': target_in_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_in_DB_log = None
            target_in_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_in_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_in_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_in_DB_log,
                                                    'target': target_in_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_in_pol_limit = None
            target_in_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_in_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_in_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'pol',
                                                    'style': 'endArrow=classic', 'source': source_in_pol_limit,
                                                    'target': target_in_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_in_pol_out_request = None
            target_in_pol_out_request = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_in_pol_out_request = value['id']
                    first_condition = True
                if value['type'] == 'reason' and value['for_process'] == str(data_flow_typed['target']):
                    target_in_pol_out_request = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'pol',
                                                    'style': 'endArrow=classic', 'source': source_in_pol_out_request,
                                                    'target': target_in_pol_out_request, 'type': 'reqrea',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_in_limit_process = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_in_limit_process = value['id']
                    break
            dfd_graph_typed[index] = {'id': index, 'value': data_flow_typed['value'] + '?', 'style': 'endArrow=classic',
                                      'source': source_in_limit_process,
                                      'target': data_flow_typed['target'], 'type': 'limpro',
                                      'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            # DB_pol_counter = DB_pol_counter+1
            # clean_counter = clean_counter+1

        # transform the 'inc' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'inc':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_in_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_in_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': data_flow_typed['value'],
                                                    'style': 'endArrow=classic', 'source': data_flow_typed['source'],
                                                    'target': target_in_limit, 'type': 'extlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            target_in_request = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_in_request = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'pol',
                                                    'style': 'endArrow=classic', 'source': data_flow_typed['source'],
                                                    'target': target_in_request, 'type': 'extreq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_in_log = None
            target_in_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_in_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_in_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_in_log,
                                                    'target': target_in_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_in_DB_log = None
            target_in_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_in_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_in_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_in_DB_log,
                                                    'target': target_in_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_in_pol_limit = None
            target_in_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_in_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_in_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'pol',
                                                    'style': 'endArrow=classic', 'source': source_in_pol_limit,
                                                    'target': target_in_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_in_limit_comp_process = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_in_limit_comp_process = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_in_limit_comp_process,
                                                    'target': data_flow_typed['target'], 'type': 'reqcpro',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_in_limit_comp_process = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_in_limit_comp_process = value['id']
                    break
            dfd_graph_typed[index] = {'id': index, 'value': data_flow_typed['value'] + '?', 'style': 'endArrow=classic',
                                      'source': source_in_limit_comp_process,
                                      'target': data_flow_typed['target'], 'type': 'limcpro',
                                      'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            # DB_pol_counter = DB_pol_counter+1
            # clean_counter = clean_counter+1

        # transform the 'out' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'out':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_out_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_out_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'], 'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_out_limit, 'type': 'porlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_out_request = None
            target_out_request = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'reason' and value['for_process'] == str(data_flow_typed['source']):
                    source_out_request = value['id']
                    first_condition = True
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_out_request = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_out_request,
                                                    'target': target_out_request, 'type': 'reareq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_out_log = None
            target_out_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_out_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_out_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_out_log,
                                                    'target': target_out_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_out_DB_log = None
            target_out_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_out_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_out_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_out_DB_log,
                                                    'target': target_out_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_out_pol_limit = None
            target_out_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_out_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_out_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_out_pol_limit,
                                                    'target': target_out_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_out_pol_out_request = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_out_pol_out_request = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_out_pol_out_request,
                                                    'target': data_flow_typed['target'], 'type': 'reqext',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_out_limit_external_entity = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_out_limit_external_entity = value['id']
                    break
            dfd_graph_typed[index] = {'id': index, 'value': data_flow_typed['value'] + '?', 'style': 'endArrow=classic',
                                      'source': source_out_limit_external_entity,
                                      'target': data_flow_typed['target'], 'type': 'limext',
                                      'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            # DB_pol_counter = DB_pol_counter+1
            # clean_counter = clean_counter+1

        # transform the 'outc' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'outc':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_out_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_out_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'], 'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_out_limit, 'type': 'cprolim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            target_out_request = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_out_request = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'pol',
                                                    'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_out_request, 'type': 'cproreq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_out_log = None
            target_out_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_out_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_out_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_out_log,
                                                    'target': target_out_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_out_DB_log = None
            target_out_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_out_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_out_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_out_DB_log,
                                                    'target': target_out_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_out_pol_limit = None
            target_out_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_out_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_out_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_out_pol_limit,
                                                    'target': target_out_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_out_pol_out_request = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_out_pol_out_request = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_out_pol_out_request,
                                                    'target': data_flow_typed['target'], 'type': 'reqext',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_out_limit_external_entity = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_out_limit_external_entity = value['id']
                    break
            dfd_graph_typed[index] = {'id': index, 'value': data_flow_typed['value'] + '?',
                                      'style': 'endArrow=classic',
                                      'source': source_out_limit_external_entity,
                                      'target': data_flow_typed['target'], 'type': 'limext',
                                      'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            # DB_pol_counter = DB_pol_counter+1
            # clean_counter = clean_counter+1

        # transform the 'store' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'store':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new elements
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'clean %d' % clean_counter,
                                                    'style': 'ellipse', 'source': 'null', 'target': 'null',
                                                    'type': 'clean', 'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # add the new data flow
            target_store_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_store_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'], 'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_store_limit, 'type': 'porlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_request = None
            target_store_request = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'reason' and value['for_process'] == str(data_flow_typed['source']):
                    source_store_request = value['id']
                    first_condition = True
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_store_request = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_store_request,
                                                    'target': target_store_request, 'type': 'resreq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_pol_out_request = None
            target_store_pol_out_request = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_store_pol_out_request = value['id']
                    first_condition = True
                if value['type'] == 'pol_DB' and value['for_DB'] == str(data_flow_typed['target']):
                    target_store_pol_out_request = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_store_pol_out_request,
                                                    'target': target_store_pol_out_request,
                                                    'type': 'reqpdb',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # changed this to request -> limit
            source_store_pol_limit = None
            target_store_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_store_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_store_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_store_pol_limit,
                                                    'target': target_store_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_log = None
            target_store_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_store_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_store_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_store_log,
                                                    'target': target_store_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_DB_log = None
            target_store_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_store_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_store_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_store_DB_log,
                                                    'target': target_store_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_pol_clean = None
            target_store_pol_clean = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'pol_DB' and value['for_DB'] == str(data_flow_typed['target']):
                    source_store_pol_clean = value['id']
                    first_condition = True
                if value['type'] == 'clean' and value['value'].endswith(str(clean_counter)):
                    target_store_pol_clean = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_store_pol_clean,
                                                    'target': target_store_pol_clean, 'type': 'pdbcle',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_ref_clean = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'clean' and value['value'].endswith(str(clean_counter)):
                    source_store_ref_clean = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'ref', 'style': 'endArrow=cross',
                                                    'source': source_store_ref_clean,
                                                    'target': data_flow_typed['target'], 'type': 'cledb_del',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_limit_data_base = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_store_limit_data_base = value['id']
                    break
            dfd_graph_typed[index] = {'id': index, 'value': data_flow_typed['value'] + '?', 'style': 'endArrow=classic',
                                      'source': source_store_limit_data_base,
                                      'target': data_flow_typed['target'], 'type': 'limdb',
                                      'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            DB_pol_counter = DB_pol_counter + 1
            clean_counter = clean_counter + 1

        # transform the 'cstore' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'cstore':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new elements
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'clean %d' % clean_counter,
                                                    'style': 'ellipse', 'source': 'null', 'target': 'null',
                                                    'type': 'clean', 'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # add the new data flow
            target_store_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_store_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'], 'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_store_limit, 'type': 'cprolim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            target_store_request = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_store_request = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'pol',
                                                    'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_store_request, 'type': 'cproreq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_pol_out_request = None
            target_store_pol_out_request = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_store_pol_out_request = value['id']
                    first_condition = True
                if value['type'] == 'pol_DB' and value['for_DB'] == str(data_flow_typed['target']):
                    target_store_pol_out_request = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_store_pol_out_request,
                                                    'target': target_store_pol_out_request,
                                                    'type': 'reqpdb', 'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # changed this to request -> limit
            source_store_pol_limit = None
            target_store_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_store_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_store_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_store_pol_limit,
                                                    'target': target_store_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_log = None
            target_store_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_store_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_store_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_store_log,
                                                    'target': target_store_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_DB_log = None
            target_store_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_store_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_store_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_store_DB_log,
                                                    'target': target_store_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_pol_clean = None
            target_store_pol_clean = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'pol_DB' and value['for_DB'] == str(data_flow_typed['target']):
                    source_store_pol_clean = value['id']
                    first_condition = True
                if value['type'] == 'clean' and value['value'].endswith(str(clean_counter)):
                    target_store_pol_clean = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_store_pol_clean,
                                                    'target': target_store_pol_clean, 'type': 'pdbcle',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_ref_clean = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'clean' and value['value'].endswith(str(clean_counter)):
                    source_store_ref_clean = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'ref', 'style': 'endArrow=cross',
                                                    'source': source_store_ref_clean,
                                                    'target': data_flow_typed['target'], 'type': 'cledb_del',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_store_limit_data_base = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_store_limit_data_base = value['id']
                    break
            dfd_graph_typed[index] = {'id': index, 'value': data_flow_typed['value'] + '?',
                                      'style': 'endArrow=classic',
                                      'source': source_store_limit_data_base,
                                      'target': data_flow_typed['target'], 'type': 'limdb',
                                      'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            DB_pol_counter = DB_pol_counter + 1
            clean_counter = clean_counter + 1

        # transform the 'read' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'read':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_read_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_read_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'],
                                                    'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_read_limit, 'type': 'dblim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_read_request = None
            target_read_request = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'pol_DB' and value['for_DB'] == str(data_flow_typed['source']):
                    source_read_request = value['id']
                    first_condition = True
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_read_request = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_read_request,
                                                    'target': target_read_request, 'type': 'pdbreq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_read_pol_limit = None
            target_read_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_read_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_read_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_read_pol_limit,
                                                    'target': target_read_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_read_log = None
            target_read_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_read_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_read_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_read_log,
                                                    'target': target_read_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_read_DB_log = None
            target_read_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_read_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_read_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_read_DB_log,
                                                    'target': target_read_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # *** something wrong here ***
            source_read_pol_out_request = None
            target_read_pol_out_request = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_read_pol_out_request = value['id']
                    first_condition = True
                if value['type'] == 'reason' and value['for_process'] == str(data_flow_typed['target']):
                    target_read_pol_out_request = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_read_pol_out_request,
                                                    'target': target_read_pol_out_request,
                                                    'type': 'reqrea',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_read_limit_process = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_read_limit_process = value['id']
                    break
            dfd_graph_typed[index] = {'id': index, 'value': data_flow_typed['value'] + '?', 'style': 'endArrow=classic',
                                      'source': source_read_limit_process,
                                      'target': data_flow_typed['target'], 'type': 'limpro',
                                      'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            # DB_pol_counter = DB_pol_counter+1
            # clean_counter = clean_counter+1

        # transform the 'cread' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'cread':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_read_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_read_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'],
                                                    'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_read_limit, 'type': 'dblim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_read_request = None
            target_read_request = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'pol_DB' and value['for_DB'] == str(data_flow_typed['source']):
                    source_read_request = value['id']
                    first_condition = True
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_read_request = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_read_request,
                                                    'target': target_read_request, 'type': 'pdbreq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_read_pol_limit = None
            target_read_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_read_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_read_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_read_pol_limit,
                                                    'target': target_read_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_read_log = None
            target_read_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_read_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_read_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_read_log,
                                                    'target': target_read_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_read_DB_log = None
            target_read_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_read_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_read_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_read_DB_log,
                                                    'target': target_read_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_read_pol_out_request = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_read_pol_out_request = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_read_pol_out_request,
                                                    'target': data_flow_typed['target'], 'type': 'reqcpro',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_read_limit_composite_process = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_read_limit_composite_process = value['id']
                    break
            dfd_graph_typed[index] = {'id': index, 'value': data_flow_typed['value'] + '?',
                                      'style': 'endArrow=classic',
                                      'source': source_read_limit_composite_process,
                                      'target': data_flow_typed['target'], 'type': 'limcpro',
                                      'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            # DB_pol_counter = DB_pol_counter+1
            # clean_counter = clean_counter+1

        # transform the 'delete' type of data flow
        if data_flow_typed['style'] == 'endArrow=cross' and data_flow_typed['type'] == 'delete':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_del_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_del_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'ref (%s)' % data_flow_typed['value'],
                                                    'style': 'endArrow=classic', 'source': data_flow_typed['source'],
                                                    'target': target_del_limit, 'type': 'prolim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_del_request = None
            target_del_request = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'reason' and value['for_process'] == str(data_flow_typed['source']):
                    source_del_request = value['id']
                    first_condition = True
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_del_request = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_del_request,
                                                    'target': target_del_request, 'type': 'reareq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_del_pol_limit = None
            target_del_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_del_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_del_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_del_pol_limit,
                                                    'target': target_del_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_del_log = None
            target_del_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_del_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_del_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'ref  (%s)' % data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_del_log,
                                                    'target': target_del_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_del_DB_log = None
            target_del_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_del_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_del_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'ref  (%s)' % data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_del_DB_log,
                                                    'target': target_del_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_del_pol_out_request = None
            target_del_pol_out_request = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_del_pol_out_request = value['id']
                    first_condition = True
                if value['type'] == 'pol_DB' and value['for_DB'] == str(data_flow_typed['target']):
                    target_del_pol_out_request = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_del_pol_out_request,
                                                    'target': target_del_pol_out_request,
                                                    'type': 'reqpdb',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_del_data_base = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_del_data_base = value['id']
                    break
            dfd_graph_typed[index] = {'id': index, 'value': 'ref  (%s) ?' % data_flow_typed['value'],
                                      'style': 'endArrow=cross', 'source': source_del_data_base,
                                      'target': data_flow_typed['target'], 'type': 'limdb_del',
                                      'DFD_element_id': index}
            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            # DB_pol_counter = DB_pol_counter+1
            # clean_counter = clean_counter+1

        # transform the 'cdelete' type of data flow
        if data_flow_typed['style'] == 'endArrow=cross' and data_flow_typed['type'] == 'cdelete':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_del_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_del_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'ref (%s)' % data_flow_typed['value'],
                                                    'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_del_limit, 'type': 'cprolim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            target_del_request = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_del_request = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol',
                                                    'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_del_request, 'type': 'cproreq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_del_pol_limit = None
            target_del_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_del_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_del_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_del_pol_limit,
                                                    'target': target_del_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_del_log = None
            target_del_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_del_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_del_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'ref  (%s)' % data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_del_log,
                                                    'target': target_del_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_del_DB_log = None
            target_del_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_del_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_del_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'ref  (%s)' % data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic', 'source': source_del_DB_log,
                                                    'target': target_del_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_del_pol_out_request = None
            target_del_pol_out_request = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_del_pol_out_request = value['id']
                    first_condition = True
                if value['type'] == 'pol_DB' and value['for_DB'] == str(data_flow_typed['target']):
                    target_del_pol_out_request = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_del_pol_out_request,
                                                    'target': target_del_pol_out_request,
                                                    'type': 'reqpdb',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_del_data_base = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_del_data_base = value['id']
                    break
            dfd_graph_typed[index] = {'id': index, 'value': 'ref  (%s) ?' % data_flow_typed['value'],
                                      'style': 'endArrow=cross', 'source': source_del_data_base,
                                      'target': data_flow_typed['target'], 'type': 'limdb_del',
                                      'DFD_element_id': index}
            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            # DB_pol_counter = DB_pol_counter+1
            # clean_counter = clean_counter+1

        # transform the 'comp' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'comp':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_comp_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_comp_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'], 'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_comp_limit, 'type': 'prolim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # value of the pol should be the updated one which is related to updated data
            source_comp_reason = None
            target_comp_reason = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'reason' and value['for_process'] == str(data_flow_typed['source']):
                    source_comp_reason = value['id']
                    first_condition = True
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_comp_reason = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_comp_reason,
                                                    'target': target_comp_reason, 'type': 'reareq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_log = None
            target_comp_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_comp_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_comp_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_log,
                                                    'target': target_comp_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_DB_log = None
            target_comp_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_comp_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_comp_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_DB_log,
                                                    'target': target_comp_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # updated pol here that generated from reason of the sources process of this comp flow type
            source_comp_pol_limit = None
            target_comp_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_comp_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_comp_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_comp_pol_limit,
                                                    'target': target_comp_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # updated pol here that generated from reason of the sources process of this comp flow type
            source_comp_request_reason = None
            target_comp_request_reason = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_comp_request_reason = value['id']
                    first_condition = True
                if value['type'] == 'reason' and value['for_process'] == str(data_flow_typed['target']):
                    target_comp_request_reason = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'pol',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_request_reason,
                                                    'target': target_comp_request_reason,
                                                    'type': 'reqrea', 'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_limit_process = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_comp_limit_process = value['id']
                    break
            dfd_graph_typed[index] = {'id': index,
                                      'value': data_flow_typed['value'] + '?',
                                      'style': 'endArrow=classic',
                                      'source': source_comp_limit_process,
                                      'target': data_flow_typed['target'],
                                      'type': 'limpro', 'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            DB_pol_counter = DB_pol_counter + 1
            clean_counter = clean_counter + 1

        # transform the 'ccomp' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'ccomp':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_comp_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_comp_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'], 'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_comp_limit, 'type': 'cprolim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            target_comp_request = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_comp_request = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_comp_request, 'type': 'cproreq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_log = None
            target_comp_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_comp_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_comp_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_log,
                                                    'target': target_comp_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_DB_log = None
            target_comp_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_comp_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_comp_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_DB_log,
                                                    'target': target_comp_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # updated pol here that generated from reason of the sources process of this comp flow type
            source_comp_pol_limit = None
            target_comp_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_comp_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_comp_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_comp_pol_limit,
                                                    'target': target_comp_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # updated pol here that generated from reason of the sources process of this comp flow type
            source_comp_request_reason = None
            target_comp_request_reason = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_comp_request_reason = value['id']
                    first_condition = True
                if value['type'] == 'reason' and value['for_process'] == str(data_flow_typed['target']):
                    target_comp_request_reason = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'pol',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_request_reason,
                                                    'target': target_comp_request_reason,
                                                    'type': 'reqrea', 'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_limit_process = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_comp_limit_process = value['id']
                    break
            dfd_graph_typed[index] = {'id': index,
                                      'value': data_flow_typed['value'] + '?',
                                      'style': 'endArrow=classic',
                                      'source': source_comp_limit_process,
                                      'target': data_flow_typed['target'],
                                      'type': 'limpro', 'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            DB_pol_counter = DB_pol_counter + 1
            clean_counter = clean_counter + 1

        # transform the 'compc' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'compc':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_comp_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_comp_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'], 'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_comp_limit, 'type': 'prolim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # value of the pol should be the updated one which is related to updated data
            source_comp_reason = None
            target_comp_reason = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'reason' and value['for_process'] == str(data_flow_typed['source']):
                    source_comp_reason = value['id']
                    first_condition = True
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_comp_reason = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_comp_reason,
                                                    'target': target_comp_reason, 'type': 'reareq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_log = None
            target_comp_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_comp_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_comp_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_log,
                                                    'target': target_comp_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_DB_log = None
            target_comp_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_comp_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_comp_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_DB_log,
                                                    'target': target_comp_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # updated pol here that generated from reason of the sources process of this comp flow type
            source_comp_pol_limit = None
            target_comp_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_comp_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_comp_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_comp_pol_limit,
                                                    'target': target_comp_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_request_composite_process = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_comp_request_composite_process = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'pol',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_request_composite_process,
                                                    'target': data_flow_typed['target'],
                                                    'type': 'reqcpro', 'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_limit_composite_process = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_comp_limit_composite_process = value['id']
                    break
            dfd_graph_typed[index] = {'id': index,
                                      'value': data_flow_typed['value'] + '?',
                                      'style': 'endArrow=classic',
                                      'source': source_comp_limit_composite_process,
                                      'target': data_flow_typed['target'],
                                      'type': 'limcpro', 'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            DB_pol_counter = DB_pol_counter + 1
            clean_counter = clean_counter + 1

        # transform the 'ccompc' type of data flow
        if data_flow_typed['style'] == 'endArrow=classic' and data_flow_typed['type'] == 'ccompc':
            # add the new elements (common entities)
            dfd_graph_typed, len_of_dfd_elements = add_common_entities_pa_dfd(dfd_graph_typed, len_of_dfd_elements,
                                                                              limit_counter, request_counter,
                                                                              log_counter, DB_log_counter, index)
            # add the new data flow
            target_comp_limit = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_comp_limit = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'], 'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_comp_limit, 'type': 'cprolim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            target_comp_request = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    target_comp_request = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': data_flow_typed['source'],
                                                    'target': target_comp_request, 'type': 'cproreq',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_log = None
            target_comp_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_comp_log = value['id']
                    first_condition = True
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    target_comp_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_log,
                                                    'target': target_comp_log, 'type': 'limlog',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_DB_log = None
            target_comp_DB_log = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'log' and value['value'].endswith(str(log_counter)):
                    source_comp_DB_log = value['id']
                    first_condition = True
                if value['type'] == 'DB_log' and value['value'].endswith(str(DB_log_counter)):
                    target_comp_DB_log = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': data_flow_typed['value'] + ',pol' + ',v',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_DB_log,
                                                    'target': target_comp_DB_log, 'type': 'logging',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            # updated pol here that generated from reason of the sources process of this comp flow type
            source_comp_pol_limit = None
            target_comp_pol_limit = None
            first_condition = False
            second_condition = False
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_comp_pol_limit = value['id']
                    first_condition = True
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    target_comp_pol_limit = value['id']
                    second_condition = True
                if first_condition and second_condition:
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements,
                                                    'value': 'pol', 'style': 'endArrow=classic',
                                                    'source': source_comp_pol_limit,
                                                    'target': target_comp_pol_limit, 'type': 'reqlim',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_request_composite_process = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'request' and value['value'].endswith(str(request_counter)):
                    source_comp_request_composite_process = value['id']
                    break
            dfd_graph_typed[len_of_dfd_elements] = {'id': len_of_dfd_elements, 'value': 'pol',
                                                    'style': 'endArrow=classic',
                                                    'source': source_comp_request_composite_process,
                                                    'target': data_flow_typed['target'],
                                                    'type': 'reqcpro',
                                                    'DFD_element_id': index}
            len_of_dfd_elements = len_of_dfd_elements + 1

            source_comp_limit_composite_process = None
            for key, value in dfd_graph_typed.items():
                if value['type'] == 'limit' and value['value'].endswith(str(limit_counter)):
                    source_comp_limit_composite_process = value['id']
                    break
            dfd_graph_typed[index] = {'id': index,
                                      'value': data_flow_typed['value'] + '?',
                                      'style': 'endArrow=classic',
                                      'source': source_comp_limit_composite_process,
                                      'target': data_flow_typed['target'],
                                      'type': 'limcpro', 'DFD_element_id': index}

            limit_counter = limit_counter + 1
            request_counter = request_counter + 1
            log_counter = log_counter + 1
            DB_log_counter = DB_log_counter + 1
            DB_pol_counter = DB_pol_counter + 1
            clean_counter = clean_counter + 1

    return dfd_graph_typed


def generate_padfd_and_tracking_maps(csvfile_dfd, csvfile_tracking_maps, csvfile_padfd):
    dic_dfd = generate_dfd_dic(csvfile_dfd)
    nested_dic_dfd = generate_dfd_nested_dic(dic_dfd)
    dfd_with_flow_types = get_dfd_flow_types(nested_dic_dfd)

    dfd_with_target_types = typed_dfd_with_target_types(dfd_with_flow_types)
    generate_dfd_csv_with_target_types(dfd_with_target_types, csvfile_tracking_maps)

    pa_dfd_graph = generate_pa_dfd(dfd_with_flow_types)
    csv_columns = ['id', 'value', 'style', 'source', 'target', 'type', 'target_type', 'for_process', 'for_DB',
                   'DFD_element_id']
    csv_pa_dfd_file = csvfile_padfd
    try:
        with open(csv_pa_dfd_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for key, data in pa_dfd_graph.items():
                writer.writerow(data)
    except IOError:
        print("I/O error")


dfd_xml_filename = sys.argv[1]
dfd_csv_filename = sys.argv[2]
pa_dfd_csv_filename = sys.argv[3]
tracking_maps_csv_filename = sys.argv[4]

initialize(dfd_xml_filename, dfd_csv_filename)
generate_padfd_and_tracking_maps(dfd_csv_filename, tracking_maps_csv_filename, pa_dfd_csv_filename)


# --------------- creating DFD with target info (ids)----------------- #

def add_padfd_ids_to_dfd(dfd_csv, padfd_csv):
    with open(dfd_csv) as dfd_csv_file:
        dfd_data = csv.DictReader(dfd_csv_file)
        dfd_data_list = [row for row in dfd_data]
    with open(padfd_csv) as padfd_csv_file:
        padfd_data = csv.DictReader(padfd_csv_file)
        padfd_data_list = [row for row in padfd_data]
        for padfd_element in padfd_data_list:
            for dfd_element in dfd_data_list:
                if padfd_element['DFD_element_id'] == dfd_element['id']:
                    if 'target_id' in dfd_element.keys():
                        dfd_element['target_id'].append(padfd_element['id'])
                    else:
                        dfd_element['target_id'] = [padfd_element['id']]
        return dfd_data_list


def generate_dfd_csv_with_target_info(dfd_with_target_info, tracking_maps_csv):
    csv_columns = ['id', 'value', 'style', 'source', 'target', 'type', 'DFD_element_id', 'target_type', 'target_id']
    DFD_targets_info = tracking_maps_csv
    try:
        with open(DFD_targets_info, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dfd_with_target_info:
                writer.writerow(data)
    except IOError:
        print("I/O error")


dfd_with_target_types_and_ids = add_padfd_ids_to_dfd(tracking_maps_csv_filename, pa_dfd_csv_filename)
generate_dfd_csv_with_target_info(dfd_with_target_types_and_ids, tracking_maps_csv_filename)

