import sys

[sys.path.append(i) for i in ['..']]

from flask import Flask, json, request
from flask import redirect # JAT added this to try and link to NLPDocTool

app = Flask(__name__)

from process_data import parse_options_into_db, find_pretrained_models, select_some, save_to_csv, write_to_csv, write_to_csv_annotations, load_csv_to_json_object, get_label_counts, sort_label_counts, tableify_label_statistics, parse_annotation_data, get_summary_rows, custom_save_to_csv
from database import instantiate_tables, fill_tables, get_options, get_option, get_option_data, set_annotation_data, get_annotation_data, create_constants, set_constants, get_constant, add_labels, get_label_set, get_table_rows_full, get_table_rows, get_labeled_data, get_unlabeled_data, get_label_set_data, create_labels

from training.finetune_model import open_coding_finetune_model

from training.predict_labels import call_predict
from training.generate_pretrained_model import call_pretrain_model_distilbert_local

from tqdm import tqdm as tq
import os

DO_FINETUNING_BOOL = True
# usage: we're just doing a demo and relabeling everything would be pointless
DO_LABELING_BOOL = False 

# normal constants
GROUP_CSV_FIELDNAMES = ["id", "text", "annotation", "true_label"]

@app.route('/', methods=['GET'])
def test():
    
    response = {
        "body": "welcome to the OpenCodingForMachineLearning Flask Server"
    }

    add_options(response)
    return json.jsonify(response)

# initialize endpoints to NLPDocTool
@app.route('/DocTool', methods=['GET'])
def doc_tool_home():
    response = {
        "body": "Welcome to the DocTool Home Page!"
    }
    add_options(response)
    # not sure if we can redirect(https://docforml.github.io/NLPDocTool) as well
    # but this is the bare bones attempt
    return json.jsonify(response)

@app.route('/DocTool/step1', methods=['GET'])
def doc_tool_step1():
    # this doesn't work because we must have been to the home page first 
    # attempt 1: return redirect('https://docforml.github.io/NLPDocTool/')
    # then I realized I need to be doing this in the frontend
    response = {
        "body": "Now at DocTool *Step1* Page!"
    }
    add_options(response)
    return json.jsonify(response)

@app.route('/data/prep_data', methods=['GET'])
def prep_data():
    '''
    A request to grab all csv files, and load the information into the database
    '''
    # I imagine this is where the trouble is coming from,
    # since our SQLite database files aren't here yet, this won't work anyway.
    
    # data_dict = parse_options_into_db()
    # find_pretrained_models(data_dict)

    # instantiate_tables(data_dict)
    # fill_tables(data_dict)

    response = {
        "body": "ok"
    }

    add_options(response)
    return json.jsonify(response)
    

@app.route('/data/get_all_data_options', methods=['GET'])
def get_all_data_options():
    '''
    A request to get all dataset options.
    '''
    options = get_options()
    create_constants()

    response = {
        "names": [options[option]["name"] for option in options],
        "options": options,
        # "pretrained_models": {options[option]["name"]: options[option]["models"] for option in options}
    }

    add_options(response)
    return json.jsonify(response)


# TODO: based on selected data option, might have to pre-train the model
@app.route('/data/get_data_option', methods=['GET'])
def get_data_option():
    '''
    A request to get data for a particular dataset option. 
    '''

    option_id = request.args.get("id")
    # in same order as defined constants table
    constants = request.args.get("constants").split(',')
    numeric_constants = tuple(map(lambda k: int(k), constants[:5]))
    model = constants[5]

    max_request_size = numeric_constants[0] # NOTE: this constant adjusts the number of rows to annotate during open coding
    
    # get the selected data and initialize necessary tables
    options = get_option_data(option_id)
    create_labels(option_id)
    set_constants(numeric_constants, model)
    
    # choose a subset of rows to return at random
    option_ids = list(options.keys())
    selected_ids = select_some(option_ids, 0, max_request_size)

    parsed_options = []
    for id in selected_ids:
        parsed_options.append({"id": int(id), "text": options[id]["text"], "annotation": options[id]["annotation"]})

    response = {
        "rows": parsed_options
    }

    add_options(response)
    return json.jsonify(response)


@app.route('/data/save_annotations', methods=['POST'])
def save_annotations():
    '''
    Saves annotation rows for a particular dataset option.
    '''
    response = {}
    add_options(response)
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json_data = request.get_json()

        rows = json_data['rows']
        option_id = json_data['id']

        set_annotation_data(option_id, rows)
        
        response['msg'] = 'Success'
    else:
        response['msg'] = 'Content-Type not supported!'
        response['ok'] = False
    
    return json.jsonify(response)


@app.route('/data/get_annotations', methods=['GET'])
def get_annotations():
    '''
    Gets annotation rows for a particular dataset option.
    '''
    option_id = request.args.get("id")
    annotations = get_annotation_data(option_id)

    parsed_options = parse_annotation_data(annotations)
    response = {
        "rows": parsed_options
    }

    add_options(response)
    return json.jsonify(response)

# TODO: update rows to include prediction
@app.route('/data/save_labels', methods=['POST'])
def save_labels():
    '''
    Saves labels for a particular dataset option.
    '''
    response = {}
    add_options(response)
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json_data = request.get_json()

        rows = json_data['rows']
        option_id = json_data['id']

        add_labels(option_id, rows)
        response['msg'] = 'Success'
    else:
        response['msg'] = 'Content-Type not supported!'
        response['ok'] = False

    return json.jsonify(response)


@app.route('/data/get_label_set', methods=['GET'])
def get_label_set_req():
    '''
    Gets the set of labels currently associated with a particular dataset option.
    '''
    option_id = request.args.get("id")
    label_set = get_label_set(option_id)

    response = {
        "rows": label_set
    }

    add_options(response)
    return json.jsonify(response)

# TODO: function for extracting prediction accuracy for open coding


@app.route('/data/pretrain_model', methods=['POST'])
def pretrain_model():
    '''
    Pretrains a new model for the given data set option using the specifed parameters.
    The new model canbe found under ./training/models.

    Returns the new model's directory name.
    '''
    response = {}
    add_options(response)
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json_data = request.get_json()

        batch_size = json_data['batch_size']
        num_epochs = json_data['num_epochs']
        option_id = json_data['id']

        # fetch desired dataset name from option_id
        input_filename = '_'.join(get_option(option_id).lower().split(' '))
        input_path = './../data/'
        output_path = './../training/models/'

        # pretrain pretrain
        output_filename = call_pretrain_model_distilbert_local(input_filename, int(batch_size), int(num_epochs), input_path, output_path)

        response['model'] = output_filename
        response['msg'] = 'Success'
    else:
        response['msg'] = 'Content-Type not supported!'
        response['ok'] = False

    return json.jsonify(response)

@app.route('/data/train_and_predict', methods=['POST'])
def train_and_predict():
    '''
    Initiates one loop of the train and predict feedback loop.

    Saves the labels provided and succesively re-trains the appropriate classification model. Then, 
    gathers a group of predicted labels for un-seen text examples and returns them for future classification.
    '''
    response = {}
    add_options(response)
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json_data = request.get_json()

        rows = json_data['rows']
        option_id = json_data['id']

        # save the new labels
        add_labels(option_id, rows)

        # get row ids and build up required data rows
        row_ids = [row['id'] for row in rows]
        text_objs = get_table_rows_full(option_id, row_ids)
        data_rows = [{'text': text_objs[elem['id']]['text'], 'id': elem['id'], 'label': elem['true_label']} for elem in rows]

        # grab which model we're going to use in order to support successive training (efficiency booster)
        model_type = json_data['model']
        model_name = get_constant('model')
        # model_name = 'happy_db_pretrained_50_5' if (model_type == 0) else 'open_coding_finetuned_1_1_1_' + 'happy_db_pretrained_50_5'
        model_name = model_name if (model_type == 0) else 'open_coding_finetuned_1_1_1_' + model_name

        percent_train = 1 # always use entire set to train
        # NOTE: These parameters are adjustable
        batch_size = get_constant('batch_size')
        num_epochs = get_constant('num_epochs')

        # gather label_id_mappings
        id_label_tuples = get_label_set_data(option_id)
        label_id_mappings = {
            'id_to_label': {},
            'label_to_id': {}
        }
        for id, label in id_label_tuples:
            label_id_mappings['id_to_label'][id] = label
            label_id_mappings['label_to_id'][label] = id

        # finetune the model, return output filepath
        output_name = open_coding_finetune_model(model_name, label_id_mappings, ([d['text'] for d in data_rows], [d['label'] for d in data_rows]), percent_train, batch_size, num_epochs, (model_type != 0))
        
        # will be saved at the following 
        # gather all unlabeled texts
        unlabeled_data = get_unlabeled_data(option_id)

        # randomly select chosen number of examples
        number_guess = get_constant('verification')
        selected_unlabeled_data = select_some(unlabeled_data, 0.0, number_guess)

        # make predictions, return [{id, text, labels}]
        predictions = call_predict(selected_unlabeled_data, output_name, label_id_mappings)

        response["labeled"] = predictions
        response['msg'] = 'Success'
    else:
        response['msg'] = 'Content-Type not supported!'
        response['ok'] = False

    return json.jsonify(response)


@app.route('/data/get_results', methods=['GET'])
def get_results():
    '''
    Performs the final fine-tuning round with the given labels, and then enters a 
    predictive loop, where predicted labels are written to the output file in groups
    of 200, until all rows of data have been written.

    Then, returns the output filename.
    '''
    option_id = request.args.get("id")
    kerb = 'final'

    data_rows = get_labeled_data(option_id)
    model_name = get_constant('model')
    percent_train = 1 # always use entire set to train
    # NOTE: These parameters are adjustable
    batch_size = get_constant('batch_size')
    num_epochs = get_constant('num_epochs')

    # gather label_id_mappings
    id_label_tuples = get_label_set_data(option_id)
    label_id_mappings = {
        'id_to_label': {},
        'label_to_id': {}
    }
    for id, label in id_label_tuples:
        label_id_mappings['id_to_label'][id] = label
        label_id_mappings['label_to_id'][label] = id

    # finetune the model, return output filepath
    # ^ original
    # Now, i'm commenting out the finetuning.
    if not DO_FINETUNING_BOOL:
        output_name = f'open_coding_finetuned_{batch_size}_{num_epochs}_{percent_train}_{model_name}'
    else:
        output_name = open_coding_finetune_model(model_name, label_id_mappings, 
                                                 ([d['text'] for d in data_rows], [d['label'] for d in data_rows]), 
                                                 percent_train, batch_size, num_epochs)
    
    name = get_option(option_id).replace(' ', '_')

    labels_csv_file_name = kerb + '_labeled_' + name
    do_labeling_bool = DO_LABELING_BOOL
    if not do_labeling_bool:
        labels_csv_file_path = './../results/' + labels_csv_file_name + '.csv'
        if not os.path.exists(labels_csv_file_path):
            print(f"Ignoring debugging rule DO_LABELING_BOOL since output file ({labels_csv_file_path}) does not exist")
            do_labeling_bool = True

    if do_labeling_bool:
        write_to_csv(kerb + '_labeled_' + name, data_rows)

        # gather all unlabeled texts, and predict
        unlabeled_data = get_unlabeled_data(option_id)
        initial_unlabeled_data_size = len(unlabeled_data)
        batch_size = 200
        # loop until all data has been written
        # while unlabeled_data != []:
        print("Labeling data!")
        for i in tq(range(0, initial_unlabeled_data_size, batch_size)):
            if unlabeled_data == []:
                break
            
            some_selected_data = select_some(unlabeled_data, 0, batch_size)
            predictions = call_predict(some_selected_data, output_name, label_id_mappings)

            full_labels = [{'id': pred['id'], 'true_label': pred['label'], 'predicted_label': pred['label']} for pred in predictions]

            # add all labels into the database and incrementally update results file
            add_labels(option_id, full_labels)
            write_to_csv(kerb + '_labeled_' + name, predictions, False)

            unlabeled_data = get_unlabeled_data(option_id)

        # also save annotations
        annotations = get_annotation_data(option_id)
        
        write_to_csv_annotations(kerb + '_annotations_' + name, annotations)

    response = {
        "saved": kerb + '_labeled_' + name,
        "model name": output_name,
    }

    add_options(response)
    return json.jsonify(response)


@app.route('/data/get_final_labels_and_summaries', methods=['GET'])
def get_final_labels_and_summaries():
    """
    Here I hope to extract the labels 
    that were saved from get_results in a csv file
    To send to the front end to be displayed.
    
    todo: even consider if we want to do the data processing here 
    instead of in the frontend
    """
    option_id = request.args.get("id")
    
    results_path = '../results/'
    kerb = 'final'
    name = get_option(option_id).replace(' ', '_')
    # accidentally forgot csv file extension last time
    result_labels_path = results_path + kerb + '_labeled_' + name + '.csv'
    user_groups_path = results_path + 'groups.csv'
    
    response = {
        "final_labels": [],
        "model_summary_rows": [],  # will be ready and formatted to be displayed
        
        "user_annotations": [],
        "user_summary_rows": [],
        
        "user_groups": [],
        "user_group_summary_rows": []
    }

    try:
        # gather all the labels that were evaluated and saved earlier -> summarize
        response["final_labels"] = load_csv_to_json_object(result_labels_path)
        response["model_summary_rows"] = get_summary_rows(response["final_labels"])
        
        # gather the users annotations and summarize that as well
        annotations = get_annotation_data(option_id)
        response["user_annotations"] = parse_annotation_data(annotations)
        response["user_summary_rows"] = get_summary_rows(response["user_annotations"])
        
        # fix to the json `TypeError: '<' not supported between instances of 'NoneType' and 'str'`
        # was that I forgot to specify the correct fieldnames here 
        response["user_groups"] = load_csv_to_json_object(user_groups_path, GROUP_CSV_FIELDNAMES)
        # note groups are saved as true label
        # resolved why the labels were being displayed instead of the groups,
        # i didn't pass the key_to_check to the function it needed to be passed to in process_data 
        response["user_group_summary_rows"] = get_summary_rows(response["user_groups"], key_to_check="true_label")
         
    except Exception as e:
        response["ok"] = False
        response["statusText"] = str(e)
        # print("IN EXCEPT ON GET_SUMMARY_STATS_AND_LABELS")
        # print(f"response: {response}")
        return json.jsonify(response)
    
    # print("in *SUCCESS* on GET_SUMMARY_STATS_AND_LABELS")
    # print(f"response: {response}")
    add_options(response)
    return json.jsonify(response)


@app.route("/data/save_groups", methods=['POST'])
def save_groups():
    option_id = request.args.get("id")
    response = {}
    
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        try:
            json_data = request.get_json()
            group_outputs_file_name = "groups"

            rows = json_data['rows']
            # todo: with groups, and how we want to display final results table
            # maybe add a function to match up the result labels with these that have been grouped and annotated?
            custom_save_to_csv(group_outputs_file_name, rows, GROUP_CSV_FIELDNAMES)
            
            response['msg'] = 'Success'
        except Exception as e:
            response['msg'] = str(e)
            response['ok'] = False
    else:
        response['msg'] = 'Content-Type not supported!'
        response['ok'] = False

    add_options(response)
    return json.jsonify(response)


def add_options(response):
    '''
    Sets default options for all return responses that are successful.
    '''
    response["headers"] = {"content-type": "application/json"},
    response["ok"] = True
    return response