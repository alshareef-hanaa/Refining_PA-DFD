import csv
import sys
import ast

node_types = ['process', 'data_base', 'composite_process', 'external_entity', 'limit', 'request', 'clean', 'reason',
              'log', 'DB_log', 'pol_DB']
privacy_node_types = ['limit', 'request', 'clean', 'log', 'DB_log']


def check_type(x_type, y_type):
    composite_process_subtypes = {'process', 'data_base', 'limit', 'request', 'clean', 'reason',
                                  'log', 'DB_log', 'pol_DB'}
    limcpro_subtypes = {'limdb', 'limpro', 'limext'}
    reqcpro_subtypes = {'reqpdb', 'reqrea', 'reqext'}
    cprolim_subtypes = {'dblim', 'prolim', 'extlim'}
    cproreq_subtypes = {'pdblim', 'reareq', 'extreq'}

    if y_type == 'composite_process':
        if x_type in composite_process_subtypes:
            return True
        else:
            return False
    elif y_type == 'limcpro':
        if x_type in limcpro_subtypes:
            return True
        else:
            return False
    elif y_type == 'reqcpro':
        if x_type in reqcpro_subtypes:
            return True
        else:
            return False
    elif y_type == 'cprolim':
        if x_type in cprolim_subtypes:
            return True
        else:
            return False
    elif y_type == 'cproreq':
        if x_type in cproreq_subtypes:
            return True
        else:
            return False


def generate_mapping_info(dfd_abstraction_csv_filename):
    with open(dfd_abstraction_csv_filename) as csv_file:
        dfd_abstraction = csv.DictReader(csv_file)
        dfd_abstraction_list = [row for row in dfd_abstraction]
        abstraction_info = []
        # generate abstraction info
        for c_id in dfd_abstraction_list:
            abstraction_info.append({c_id['id']: c_id['map_to']})
    return abstraction_info


def generate_padfd_target_ids_list(dfd_csv_filename):
    with open(dfd_csv_filename) as dfd_csv_file:
        dfd_data = csv.DictReader(dfd_csv_file)
        dfd_data_list = [row for row in dfd_data]
        padfd_target_ids_list = []
        for dfd_id in dfd_data_list:
            padfd_target_ids_list.append({dfd_id['id']: ast.literal_eval(dfd_id['target_id'])})
    return padfd_target_ids_list


def generate_target_types_list(dfd_csv_filename):
    with open(dfd_csv_filename) as dfd_csv_file:
        dfd_data = csv.DictReader(dfd_csv_file)
        dfd_data_list = [row for row in dfd_data]
        target_types_of_dfd_ids = []
        for dfd_id in dfd_data_list:
            target_types_of_dfd_ids.append({dfd_id['id']: ast.literal_eval(dfd_id['target_type'])})
    return target_types_of_dfd_ids


# generate lists of dicts that represent a_padfd and c_padfd elements (nodes & edges) info
def generate_padfd_list_info(padfd_csv_filename):
    with open(padfd_csv_filename) as padfd_csv_file:
        padfd_data = csv.DictReader(padfd_csv_file)
        padfd_data_list = [row for row in padfd_data]
        return padfd_data_list


flatten = lambda t: [item for sublist in t for item in sublist]


def generate_padfd_mapping_info(nodes_dfd_mapping_info, edges_dfd_mapping_info, a_padfd_target_ids_list,
                                c_padfd_target_ids_list, a_dfd_ids_target_types_list, c_dfd_ids_target_types_list,
                                a_padfd_csv_filename, c_padfd_csv_filename):
    # generate list of dicts that represent a_padfd and c-padfd elements (nodes & edges) info
    a_padfd_elements_info = generate_padfd_list_info(a_padfd_csv_filename)
    c_padfd_elements_info = generate_padfd_list_info(c_padfd_csv_filename)

    padfd_mapping_info_list = []

    # mapping nodes (no privacy nodes mapping here expect reason and policy)
    for mapping in nodes_dfd_mapping_info:
        list_c_id_padfd_target_ids = []
        list_a_id_padfd_target_ids = []
        for c_id, a_id in mapping.items():
            # get target ids for each c_id and a_id
            for c_padfd_target_ids in c_padfd_target_ids_list:
                for key, value in c_padfd_target_ids.items():
                    if key == c_id:
                        for i in value:
                            list_c_id_padfd_target_ids.append(i)
            for a_padfd_target_ids in a_padfd_target_ids_list:
                for key, value in a_padfd_target_ids.items():
                    if key == a_id:
                        for i in value:
                            list_a_id_padfd_target_ids.append(i)
            # get target types list of c_id and a_id:
            # check that the types of padfd_target_id (from padfd csv file) are equal to types of target types list in
            # dfd this just extra check that the transformation is correct !done!
            c_id_list_of_target_types = []
            for c_dfd_ids in c_dfd_ids_target_types_list:
                c_id_list_of_target_types = {k: v for k, v in c_dfd_ids.items() if k == c_id}
                c_id_list_of_target_types = [v for v in c_id_list_of_target_types.values()]
                c_id_list_of_target_types = flatten(c_id_list_of_target_types)
                if c_id_list_of_target_types: break
            a_id_list_of_target_types = []
            for a_dfd_ids in a_dfd_ids_target_types_list:
                a_id_list_of_target_types = {k: v for k, v in a_dfd_ids.items() if k == a_id}
                a_id_list_of_target_types = [v for v in a_id_list_of_target_types.values()]
                a_id_list_of_target_types = flatten(a_id_list_of_target_types)
                if a_id_list_of_target_types: break
            for c_padfd_id in list_c_id_padfd_target_ids:
                c_padfd_id_info = [item for item in c_padfd_elements_info if item['id'] == c_padfd_id]
                c_padfd_id_type = c_padfd_id_info[0]['type']
                c_padfd_id_value = c_padfd_id_info[0]['value']
                if c_padfd_id_type in c_id_list_of_target_types:
                    for a_padfd_id in list_a_id_padfd_target_ids:
                        a_padfd_id_info = [item for item in a_padfd_elements_info if item['id'] == a_padfd_id]
                        a_padfd_id_type = a_padfd_id_info[0]['type']
                        a_padfd_id_value = a_padfd_id_info[0]['value']
                        if a_padfd_id_type in a_id_list_of_target_types:
                            if c_padfd_id_type == a_padfd_id_type:
                                if c_padfd_id_type != 'pol_DB' and a_padfd_id_type != 'pol_DB':
                                    # Note: privacy nodes except reason node don't match value/label
                                    # the values of regular nodes (cpro, pro, ext, db) and reason node should be matched
                                    if c_padfd_id_value == a_padfd_id_value:
                                        padfd_mapping_info_list.append({c_padfd_id: a_padfd_id})
                                        break
                                    # may need else here Vauleerro
                                    # ('values of regular nodes don't match check label of your nodes ' )
                                else:  # pol_DB nodes
                                    padfd_mapping_info_list.append({c_padfd_id: a_padfd_id})
                                    break
                            elif check_type(c_padfd_id_type, a_padfd_id_type):
                                padfd_mapping_info_list.append({c_padfd_id: a_padfd_id})
                                break
    # mapping flows (mapping all privacy nodes)
    for mapping in edges_dfd_mapping_info:
        list_c_id_padfd_target_ids = []
        list_a_id_padfd_target_ids = []
        for c_id, a_id in mapping.items():
            if a_id != 'O':
                # first: get list of target types of c_id/a_id
                # to check if the type of each c_padfd_id/a_padfd_idare belong to c_id/a_id target types list
                c_id_list_of_target_types = []
                for c_dfd_ids in c_dfd_ids_target_types_list:
                    c_id_list_of_target_types = {k: v for k, v in c_dfd_ids.items() if k == c_id}
                    c_id_list_of_target_types = [v for v in c_id_list_of_target_types.values()]
                    c_id_list_of_target_types = flatten(c_id_list_of_target_types)
                    if c_id_list_of_target_types: break
                a_id_list_of_target_types = []
                for a_dfd_ids in a_dfd_ids_target_types_list:
                    a_id_list_of_target_types = {k: v for k, v in a_dfd_ids.items() if k == a_id}
                    a_id_list_of_target_types = [v for v in a_id_list_of_target_types.values()]
                    a_id_list_of_target_types = flatten(a_id_list_of_target_types)
                    if a_id_list_of_target_types: break
                # second: get target ids in padfd of c_id and a_id
                for c_padfd_target_ids in c_padfd_target_ids_list:
                    for key, value in c_padfd_target_ids.items():
                        if key == c_id:
                            for i in value:
                                list_c_id_padfd_target_ids.append(i)
                for a_padfd_target_ids in a_padfd_target_ids_list:
                    for key, value in a_padfd_target_ids.items():
                        if key == a_id:
                            for i in value:
                                list_a_id_padfd_target_ids.append(i)
                # Third: go through each target id of c_id and map to correct target id of a_id
                for c_padfd_id in list_c_id_padfd_target_ids:
                    # i) get info about this target id (belong to c_id)
                    c_padfd_id_info = [item for item in c_padfd_elements_info if item['id'] == c_padfd_id]
                    c_padfd_id_type = c_padfd_id_info[0]['type']
                    c_padfd_id_value = c_padfd_id_info[0]['value']
                    if c_padfd_id_type in c_id_list_of_target_types:
                        # TODO: I might need else here
                        # ii) iterate through list of a_id target ids to find match id that we can map to
                        for a_padfd_id in list_a_id_padfd_target_ids:
                            a_padfd_id_info = [item for item in a_padfd_elements_info if item['id'] == a_padfd_id]
                            a_padfd_id_type = a_padfd_id_info[0]['type']
                            a_padfd_id_value = a_padfd_id_info[0]['value']
                            if a_padfd_id_type in a_id_list_of_target_types:
                                # iv) check type matching between c_id target id and a_id target id (3 cases)
                                # Note: here we map privacy nodes (expect reason and policy) and flows as well
                                # first check if it is privacy node or flow by type
                                if c_padfd_id_type and a_padfd_id_type in privacy_node_types:  # for privacy nodes no need to check value
                                    if c_padfd_id_type == a_padfd_id_type:
                                        padfd_mapping_info_list.append({c_padfd_id: a_padfd_id})
                                        break
                                    else:
                                        continue
                                else:  # for flow (2 cases)
                                    if c_padfd_id_type == a_padfd_id_type or check_type(c_padfd_id_type,
                                                                                        a_padfd_id_type):
                                        if c_padfd_id_value == a_padfd_id_value:  # flow should have the same value/label
                                            padfd_mapping_info_list.append({c_padfd_id: a_padfd_id})
                                            break
                                    else:
                                        continue
            else:  # flow a_id was mapped to {O}
                c_id_list_of_target_types = []
                for c_dfd_ids in c_dfd_ids_target_types_list:
                    c_id_list_of_target_types = {k: v for k, v in c_dfd_ids.items() if k == c_id}
                    c_id_list_of_target_types = [v for v in c_id_list_of_target_types.values()]
                    c_id_list_of_target_types = flatten(c_id_list_of_target_types)
                    if c_id_list_of_target_types: break
                for c_padfd_target_ids in c_padfd_target_ids_list:
                    for key, value in c_padfd_target_ids.items():
                        if key == c_id:
                            for i in value:
                                list_c_id_padfd_target_ids.append(i)
                # to get cpro node that we will map all privacy nodes to
                # we need to get source of flow that has limit as target. flow type is "..lim" but not "reqlim" flow
                # this can be done also from target side
                # then check in padfd_mapping_info_list this source was mapped to which cpro node in a-padfd
                # then we map all privacy nodes to this node in a-padfd
                c_padfd_id_source_map_to = str
                for c_padfd_id in list_c_id_padfd_target_ids:
                    c_padfd_id_info = [item for item in c_padfd_elements_info if item['id'] == c_padfd_id]
                    c_padfd_id_type = c_padfd_id_info[0]['type']
                    if c_padfd_id_type.endswith('lim') and c_padfd_id_type != 'reqlim':
                        c_padfd_id_source = c_padfd_id_info[0]['source']
                        for x in padfd_mapping_info_list:
                            c_padfd_id_source_map_to = {k: v for k, v in x.items() if k == c_padfd_id_source}
                            c_padfd_id_source_map_to = c_padfd_id_source_map_to.get(c_padfd_id_source, )
                            if c_padfd_id_source_map_to:
                                break
                        break
                # by this point we found cproc node that will use to map all privacy nodes to
                for c_padfd_id in list_c_id_padfd_target_ids:
                    c_padfd_id_info = [item for item in c_padfd_elements_info if item['id'] == c_padfd_id]
                    c_padfd_id_type = c_padfd_id_info[0]['type']
                    if c_padfd_id_type in c_id_list_of_target_types:
                        if c_padfd_id_type not in privacy_node_types:  # mapping flow
                            padfd_mapping_info_list.append({c_padfd_id: 'O'})
                        else:
                            padfd_mapping_info_list.append({c_padfd_id: c_padfd_id_source_map_to})
    return padfd_mapping_info_list



# tracking_maps for each level
a_dfd_csv_filename = sys.argv[1]
a_padfd_csv_filename = sys.argv[2]
c_dfd_csv_filename = sys.argv[3]
c_padfd_csv_filename = sys.argv[4]
BDFD_nodes_abstractin = sys.argv[5]
BDFD_flows_abstractin = sys.argv[6]
# output is PA-DFDs abstraction
PADFD_abstractin_filename = sys.argv[7]

dfd_abstractin_nodes_list = generate_mapping_info(BDFD_nodes_abstractin)
dfd_abstractin_edges_list = generate_mapping_info(BDFD_flows_abstractin)
a_padfd_target_ids_list = generate_padfd_target_ids_list(a_dfd_csv_filename)
c_padfd_target_ids_list = generate_padfd_target_ids_list(c_dfd_csv_filename)
a_dfd_ids_target_types_list = generate_target_types_list(a_dfd_csv_filename)
c_dfd_ids_target_types_list = generate_target_types_list(c_dfd_csv_filename)

padfd_abstraction_info = generate_padfd_mapping_info(dfd_abstractin_nodes_list, dfd_abstractin_edges_list,
                                                     a_padfd_target_ids_list,
                                                     c_padfd_target_ids_list, a_dfd_ids_target_types_list,
                                                     c_dfd_ids_target_types_list,
                                                     a_padfd_csv_filename, c_padfd_csv_filename)


def generate_padfd_abstraction_csv(padfd_abstraction_info, PADFD_abstractin_filename):
    # csv_columns = ['id', 'map_to']
    PADFD_abstractin = PADFD_abstractin_filename
    try:
        with open(PADFD_abstractin, 'w') as csvfile:
            writer = csv.writer(csvfile)
            # writer.writeheader()
            for row in padfd_abstraction_info:
                for data in row.items():
                    writer.writerow(data)
    except IOError:
        print("I/O error")

generate_padfd_abstraction_csv(padfd_abstraction_info,PADFD_abstractin_filename)