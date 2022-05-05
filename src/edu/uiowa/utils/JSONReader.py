from edu.uiowa.parser.Tracer import Trace
import json

#import jsonschema

schema_fp = 'resources/schema.json'

def read_schema(fs):
    with open(fs, 'r') as file:
        schema = file.read().rstrip()
    #fs.close()
    return schema

def read_traces_json(df):
    benign_traces = []    
    rejected_traces = []
    AP = []

    schema = read_schema(schema_fp)
    data = None

    try:
#        f = open(df)
        # Read in the JSON document
        data = json.load(df)        
        # And validate the result
        #jsonschema.validate(data, schema)

        AP = data['propositions']
        pos_traces = data['traces_pos']
        neg_traces = data['traces_neg']
        op1 = ['!', 'Y', 'O', 'H']
        op2 = ['S','&', '|', '=>']
        #default size
        size = 3
        target_fml = None
        max_trace_len1 = 0
        max_trace_len2 = 0
        cnt = 0 
        for pt in pos_traces:
            # ndata = [[True if x == 1 else False for x in at] for at in pt]
            # neg_trace = Trace(ndata, str(cnt), AP)
            pos_trace = Trace(pt, str(cnt), AP)                
            benign_traces.append(pos_trace)
            cnt += 1

            if max_trace_len1 < len(pt):
               max_trace_len1 =  len(pt)

        for nt in neg_traces:
            neg_trace = Trace(nt, str(cnt), AP)
            rejected_traces.append(neg_trace)
            cnt += 1
            if max_trace_len2 < len(nt):
               max_trace_len2 =  len(nt)
      
        max_trace_len = max_trace_len1 if (max_trace_len1 > max_trace_len2) else max_trace_len2 
        return (AP, benign_traces, rejected_traces, op1, op2, size, target_fml, max_trace_len)

#    except jsonschema.exceptions.ValidationError as e:
#        print("well-formed but invalid JSON:", e)
    except json.decoder.JSONDecodeError as e:
        print("poorly-formed text, not JSON:", e)
    
#    return data

# if __name__ == "__main__":
#    data = parse('eas-example/eas.json')  
    #print(dict_data)
#    printf(data) 
