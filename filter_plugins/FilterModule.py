from typing import Any, Optional, Union

DOCUMENTATION = r"""
name: dict2args format output filter
author: Marek Weber <marek.weber@cloudandheat.com>, Lucas Trilken <lucas.trilken@cloudandheat.com>
version_added: "1.0.1"
short_description: Dictionary to cli arguments/options formatting output filter.
description:
- Takes single dicts and converts keys and values into arguments and options.
- When dicts are given as list, each dict on list will be converted to argument style output
- Customizable output style and key filtering.
- Supports positional arguments through single-key dicts.

options:
  input:
    description: Input dictionary/list of dictionaries.
    type: dict|list[dict]
    required: Yes
  bool2int: 
    description: If bool values should be converted to int (False => 0 or True => 1).
    type: bool
    required: No
    default: True
  str2num: 
    description: If numerical string values should be casted to appropriate numerical types.
    type: bool
    required: No
    default: False
  quote_values: 
    description: If all values should get quoted with <b>quotes</b>. (String values are always printed with quotes, to disable, set quotes="".)
    type: bool
    required: No
    default: False
  quotes: 
    description: Character(s) to use for quoting values.
    type: str
    required: No
    default: '"',
  list_sep: 
    description: Separator separating values in list values.
    type: str
    required: No
    default: ',',
  no_hyphen: 
    description: If hyphens ('-' or '--') should not get printed before argument or option names. 
    type: bool
    required: No
    default: False
  select_keys: 
    description: List of argument or option names that will be printed. (Whitelist)
    type: Optional[list[str]]
    required: No
    default: None
  reject_keys: 
    description: List of argument or option names that won't be printed. (Blacklist)
    type: Optional[list[str]]
    required: No
    default: None
    
RETURNS: Union[str, list[str]]
"""

EXAMPLES = r"""
# Basic usage
- name: Simple transformation
  debug:
    msg: "{{ demo_dict | dict2args() }}"
  vars: 
    demo_dict: {
    "pos_arg1": {
        "pos_arg2": {
            "s_arg": "Test",
            "l_arg": [1, 2.4, 3, True, False, "hello", None, "0012"],
            "b_arg": True,
            "z_arg": 0,
            "i_arg": 32768,
            "f_arg": 1.2345,
            "flag": None,
            "empty": "",
            "x": "single_letter",
            "mapping1": {
                "m1_s_arg": "Test",
                "m1_l_arg": [1, 2.4, 3, True, False, "hello", None, "0012"],
                "m1_b_arg": True,
                "m1_z_arg": 0,
                "m1_i_arg": 32768,
                "m1_f_arg": 1.2345,
                "m1_flag": None,
                "m1_empty": "",
                "x": "single_letter",
                "mapping2": {
                    "m2_s_arg": "Test",
                    "m2_l_arg": [1, 2.4, 3, True, False, "hello", None, "0012"],
                    "m2_b_arg": True,
                    "m2_z_arg": 0,
                    "m2_i_arg": 32768,
                    "m2_f_arg": 1.2345,
                    "m2_flag": None,
                    "m2_empty": "",
                    "x": "single_letter",
                    }
                }
            }
        }
    }
  # Returns: '"pos_arg1" "pos_arg2" --s_arg "Test" --l_arg 1,2.4,3,1,0,"hello",,"0012" --b_arg 1 --z_arg 0 --i_arg 32768 --f_arg 1.2345 --flag --empty -x "single_letter" --mapping1 "m1_s_arg"="Test","m1_l_arg"=1,2.4,3,1,0,"hello",,"0012","m1_b_arg"=1,"m1_z_arg"=0,"m1_i_arg"=32768,"m1_f_arg"=1.2345,"m1_flag"=,"m1_empty"=,"x"="single_letter","mapping2"="m2_s_arg"="Test","m2_l_arg"=1,2.4,3,1,0,"hello",,"0012","m2_b_arg"=1,"m2_z_arg"=0,"m2_i_arg"=32768,"m2_f_arg"=1.2345,"m2_flag"=,"m2_empty"=,"x"="single_letter"'

# With parameters
- name: Full transformation
  debug:
    msg: "{{ demo_dict | dict2args(testdict, bool2int=False, quote_values=True, quotes="/$%/", list_sep=";", no_hyphen=True, select_keys=["b_arg", "s_arg", "l_arg", "x", "i_arg" ]) }}"
  vars: 
    demo_dict: {
    "pos_arg1": {
        "pos_arg2": {
            "s_arg": "Test",
            "l_arg": [1, 2.4, 3, True, False, "hello", None, "0012"],
            "b_arg": True,
            "z_arg": 0,
            "i_arg": 32768,
            "f_arg": 1.2345,
            "flag": None,
            "empty": "",
            "x": "single_letter",
            "mapping1": {
                "m1_s_arg": "Test",
                "m1_l_arg": [1, 2.4, 3, True, False, "hello", None, "0012"],
                "m1_b_arg": True,
                "m1_z_arg": 0,
                "m1_i_arg": 32768,
                "m1_f_arg": 1.2345,
                "m1_flag": None,
                "m1_empty": "",
                "x": "single_letter",
                "mapping2": {
                    "m2_s_arg": "Test",
                    "m2_l_arg": [1, 2.4, 3, True, False, "hello", None, "0012"],
                    "m2_b_arg": True,
                    "m2_z_arg": 0,
                    "m2_i_arg": 32768,
                    "m2_f_arg": 1.2345,
                    "m2_flag": None,
                    "m2_empty": "",
                    "x": "single_letter",
                    }
                }
            }
        }
    }
  # Returns: '/$%/pos_arg1/$%/ /$%/pos_arg2/$%/ s_arg /$%/Test/$%/ l_arg /$%/1/$%/;/$%/2.4/$%/;/$%/3/$%/;/$%/true/$%/;/$%/false/$%/;/$%/hello/$%/;;/$%/0012/$%/ b_arg /$%/true/$%/ i_arg /$%/32768/$%/ x /$%/single_letter/$%/'
"""


class FilterModule(object):
    """Filter plugin container"""

    def filters(self):
        return {
            'dict2args': self.dict2args
        }

    @staticmethod
    def dict2args(input: Union[dict, list[dict]],
                  bool2int: bool = True,
                  str2num: bool = False,
                  quote_values: bool = False,
                  quotes: str = '"',
                  list_sep: str = ',',
                  no_hyphen: bool = False,
                  select_keys: Optional[list[str]] = None,
                  reject_keys: Optional[list[str]] = None) -> Union[str, list[str]]:

        if isinstance(input, list):
            return list(map(lambda _: FilterModule.dict2args(_, bool2int, str2num, quote_values, quotes, list_sep,
                                                             no_hyphen, select_keys, reject_keys), input))
        elif isinstance(input, dict):
            res = []
            # special case where first and only key of args_dict is a positional argument
            if len(input) == 1:
                args_key, args_value = next(iter(input.items()))  # get first key and value
                if isinstance(args_value, dict):
                    return FilterModule.format_value(args_key, bool2int, str2num, quote_values, quotes, list_sep) \
                        + " " + \
                        FilterModule.dict2args(args_value, bool2int, str2num, quote_values, quotes, list_sep, no_hyphen,
                                               select_keys, reject_keys)

            for arg_name, value in input.items():
                # apply key filters
                if (select_keys and arg_name not in select_keys) or (reject_keys and arg_name in reject_keys):
                    continue

                arg_name = str(arg_name)

                if not no_hyphen:
                    if len(arg_name) == 1:
                        arg_name = "-" + arg_name
                    else:
                        arg_name = "--" + arg_name

                value = FilterModule.format_value(value, bool2int, str2num, quote_values, quotes, list_sep)

                res.append(f"{arg_name} {value}" if len(value) > 0 else f"{arg_name}")

            return " ".join(res)
        else:
            return FilterModule.format_value(input, bool2int, str2num, quote_values, quotes, list_sep)

    @staticmethod
    def format_value(value: Any, bool2int: bool, str2num: bool, quote_values: bool, quotes: str, list_sep: str) -> str:
        if str2num and isinstance(value, str):
            value = FilterModule.num_or_str(value)

        if isinstance(value, list):
            if len(value) == 0:
                value = ""
            else:
                return list_sep.join(
                    map(lambda v: FilterModule.format_value(v, bool2int, str2num, quote_values, quotes, list_sep), value))
        elif isinstance(value, dict):
            return list_sep.join(
                map(lambda m: FilterModule.format_value(m[0], bool2int, str2num, quote_values, quotes, list_sep)
                              + "=" + FilterModule.format_value(m[1], bool2int, str2num, quote_values, quotes, list_sep),
                    value.items()))
        elif isinstance(value, bool):
            value = str(int(value)) if bool2int else str(value).lower()
        elif isinstance(value, str) and (value.startswith('{')):
            value="'" + value 
        elif isinstance(value, str) and (value.endswith('}')):
            value= value + "'" 
        elif value is None:
            return ""

        # handling of json here
        value = str(value)

        if quote_values and not (str(value).startswith(quotes) and str(value).endswith(quotes)):
            value = quotes + str(value) + quotes #if len(value) > 0 else ""

        if isinstance(value, str) and (value.startswith('{')):
            value="'" + value 
        if isinstance(value, str) and (value.endswith('}')):
            value= value + "'" 

        return value

    @staticmethod
    def num_or_str(value: str) -> Union[str,float,int]:
        try:
            return int(value, 0) # Guess base
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
