# Conventions for the Proxmox VE Ansible role

## Compatibility
This role was based on: https://github.com/lae/ansible-role-proxmox and the fork (https://github.com/cloudandheat/ansible-role-proxmox-ve)
We original intended to
- stay compatible with legacy inventory (variable) definitions for backwards-compatibility or
- we introduce a versioning scheme for the default variables files, which then can be easily parsed for changes.
With the decision to create a permanent fork, we might introduce breaking changes, on variable names etc.

## Structure
Structuring a complex role is a necessity to keep flexibility, therefore supporting ease of development, robustness and quality. 
### General structure
Purpose and grand goal of this role is to be a declarative (where possible) lifecycle management tool for Proxmox (clusters).
The declarative nature implies: 
- Execution shall be idempotent where state is defined.
- State of parameter variables shall directly (=bijective) relate to the state of the controlled hosts after role execution.
- Empty variables define default ('empty') state. (Default state in context of this role is defined as a fresh, unmodified installation of PVE.)
- Managed state, that is not declared in parameter variables shall be removed such that declared state is reached.
  i.e. OSDs, pools, groups, configuration, ... that exist and are not declared will be removed upon execution.
- Managed state, that is declared in parameter variables shall be created such that declared state is reached.
  i.e. OSDs, pools, groups, configuration, ... that don't exist and are declared will be created upon execution.
- When in doubt, explicitly create default state instead of relying on implicit default behavior. (Take a look at '/defaults/main.yml' for referencing all variables)

This results in some additional requirements and implications for the implementation of this role:
- Problem domains solving features should implement a destructive and a constructive sub-problem domain for their solution.
  - 'Destructive' means actions taken to reach default state from custom state.
  - 'Constructive' means actions taken to reach declared state from default state.
- That's why there must not be any explicit 'remove'/'create'/'enable'/'disable' parameter.
  The role only follows what is declared. For temporary deactivation of something, comment it out in your inventory, defaults must guarantee default state.
- Each problem domain must be defined in at least one separate task.yml file for their solution.
- Separate task files should be modular and self-contained as far as possible.
- Emphazising "Don't repeat code" at the beginning of sub-problem domains, a common validation task file might be run.
  This ensures validation before actually entering a sub-problem domain. 
  The validation should be run on every entry of the subdomain e.g. when tasks are run with tags,
  therefore the "always"-tag should be set for teh validation task. To avoid problems on unreasonable settings, 
  variables with suitable defaults are used. 
- Every task file must first validate, normalize and possibly initialize its own parameters.
- Shared parameters are validated, normalized and possibly initialized in a separate file which must include the dependent task file.
- Problem domains should be solved first by destructive and then start constructive actions, if sensible. (OSDs are an exception.)

We employ tags as a flexible way to tie different features of this role for testing during the development.
To list all tasks that will be executed on a specific tag, the options for
``` ansible-playbook [OPTIONS] -t <tag_name> --list-tasks ```can be used. 

The `tasks`-folder is further organized by nested sub-folders into the different problem-domains/features this role is solving.
Other files, like templates, should be organized in sub-folders named by their problem domain they solve, too.

The `tasks/main.yml` should be exclusively used to include/call other task files, providing the overall 'control flow' for task execution.

## Development
Some general principles we adhere to when developing this role.
### General
Solutions should be written to be as non-intrusive and update-compatible as possible.
- Tasks must guarantee that custom files are getting applied/evaluated.
- Tasks should validate custom configuration.
- Custom configuration, where needed, must be written as separate files only managed by this role and 
  only ever overwrite or change existing files if necessary.
  E.g., if 'drop-in' folders (name ending in '.d') are available, then they should be used.
- Customizations in files and custom files must be automatically removed if they are no longer needed. (Declarative approach)
- Solutions should use as few tasks as possible.
- Either some functionality is managed by this role or it is not. Edge-cases pertaining 
  potential external intervention/modification are omitted and overwritten by default.
- Don't overdo fault-tolerance. Only ever test for undefined/invalid/custom state where it is <i>actually expected</i>!
- Regex should be employed with uttermost care on preventing wrong matches and only if other ways are more complex or costly.
- Complex functionality (many tasks to solve it) which is needed multiple times should be written in Python as filter or library.
- Modularity of task files should be created through an interfaces defined by the (external) variables a task file evaluates.
  These external variables should be translated into variables of the problem domain on a `vars:`-attribute on an encompassing block scope.

### Templates
- Files that are not shared and solely managed by this role should be templated.
- Presentation must be strictly separated from computation. 
  E.g. templates should only create valid files and not implement 'business logic' by calculations wihtin the template.

### Tasks and blocks
- When querying parameters inside '`when:`' attributes to control task execution, 
  the 'default(<default value>, true)' should be used. This way, empty but still invalid values are caught.
- Parameter variables must not be tested if they're defined, they are expected to be defined or the task must fail.
- Algorithmic efficiency is highly prioritized. For example, if a costly variable transformations is needed,
  a separate 'set_fact' task should be created to execute it once and cache the result.
- Don't iterate over a variable and modify it with the '`set_fact`' at the same time.
- Tasks should never get bloated trying to solve multiple things at once which could easily be separate tasks. 
- Long statements are always broken on operators and then wrapped with the operator on the new line, 
  inheriting indentation of the previous statement part.
  ```
  CORRECT:
  <indentation> when: "long_statement_part1 + ((long_statement_part2 | default([], true))
                      + (long_statement_part3 | difference(long_statement_part4)))
  <indentation> when: "long_statement_part1 or (long_statement_part2
                      and (long_statement_part3 or not long_statement_part4))
  WRONG:
  <indentation> when: "long_statement_part1 + ((long_statement_part2 | default([], true))
  + (long_statement_part3 | difference(long_statement_part4)))
  
  <indentation> when: "long_statement_part1 or (long_statement_part2 and
                      (long_statement_part3 or not long_statement_part4))
    
  ```
  If statements still are very long, break them down into individual variables declared on the '`vars:`' attribute.

### Variables and parameters
- Variables should always encompass abstract (sub-)problems, containing only what is needed to solve its (sub-)problems, 
  not being an overfilled container or useless without many other (too small) variables.
- The 'ideal variable' structures information in itself in a way to be easily accessed/queried in subsequent dependent Ansible tasks.
  It provides exactly the information which is needed for solving a sub-problem in single or multiple tasks in itself, 
  without the need for computationally costly transformations on itself or with other variables to access needed information.
- Especially parameter variables should self-contain any information needed to solve a specific problem domain/feature and provide the necessary internal structure for it.
- When defining variables through a 'set_fact' module where the defined variable can result in undefined state,
  for example because of an empty loop, and the variable is accessed more than once through subsequent tasks, 
  the variable must be defined with an empty value through a previous 'set_fact' module first.
- Variables containing declarative information should be documented in ```defaults/main.yml``` with a comment describing the structure.

### Tests (wip/tbd)
Before commiting changes or new implementing changes, the role must be tested at least with the following use-cases: 
- Create multiple PVE hosts from scratch without clustering, with test-parameters for the changed or new feature
- Create multiple PVE cluster from scratch with Ceph enabled, including OSDs, Pools, CRUSH, CephFS, and test-parameters for the changed or new feature
- Delete a cluster node and rerun with same inventory
- Run role with minimal inventory (host variables only)
- Recreate PVE cluster with Ceph and test-parameters for the changed or new feature

Demo-playbooks and -inventories can be found in the 'Examples'-folder:
- TBA

## Styleguide and -conventions
This role follows relatively strict rules on naming, styling and structure to aim for high quality, flexibility, consistency and most importantly, readability.

1. ### Style-conventions and -rules:
   - Ansible modules are always called by their FQCN (Fully Qualified Collection Name).
   - Ansible Filters should be called by their FQCN as well.
   - Every Task and Block must have a name.
   - Tasks and blocks implementing problem domains (general features and sub-features) must be tagged by their problem domain they solve.
   - Jinja expression brackets are spaced with single whitespace after '`{{`' and before '`}}`'
   - Filter operator is always spaced with single whitespace before and after '`|`'.
   - Other brackets (e.g. list or dict initialization, filters) do not contain whitespace.
   - Strings 'yes'/'no' in any case or integer as boolean values must not be used. Only `false` and `true` are valid boolean values.
   - Usage of 'block'/'folding'/'literal' scalars ('`|`', '`|-`', '`>`', '`>-`', '\`', '-\`') for strings is discouraged,
     especially for conditional statements, but can be used for readability.
   - General rule of thumb is to quote every value, especially Jinja expressions and conditional statements!
     <br>Exceptions are: 
     - Numerical values (only when they are expected as numeric type!), e.g. '`return_code: 12`'
     - Variable declarations, e.g. '`register: _variable_name`'
     - Single boolean values, e.g. '`when: false`' or '`exclusive: true`'
     - Single specific keywords, e.g. '`state: present`'
   - Modules modifying files should declare a file owner, group and at least a file mode as (4 digit, octal number) string.
   - If multiple '`when:`' conditions apply to a task itself and as loop condition(s) on the same task,
     the task must be moved inside a new block where '`when:`' conditions are split into: 
     - block '`when:`' attribute with conditions controlling task execution
     - task '`when:`' attribute with conditions controlling loop execution. 
   - Multiple tasks that are logical part of the same functional abstraction must be grouped into blocks, 
     analogous to functions in programming.
   
   - Attributes on tasks and blocks follow a defined order for consistency and readability:
     - Order of attributes on tasks:
     ```       
     1. 'name' with descriptive task name
     2. 'become[_user|_method]', if required
     3. Fully qualified common module name
     4. Module attributes (required and common attributes first)
     5. 'register', if applicable
     6. 'args', if applicable
     7. 'vars', if any
     8. 'delegate_*', if required
     9. 'ignore_*', if required
     10. 'until', if applicable
     11. 'loop', if applicable
     12. 'loop_control', if any
     13. 'failed_when', if required
     14. 'changed_when', if required
     15. 'when', if applicable
     16. 'retries', if applicable
     17. 'delay', if applicable
     18. 'timeout', if required
     19. 'run_once', if required
     20. (others not mentioned)
     21. 'notify', if required
     22. 'check_mode', if required
     23. 'no_log', if required
     24. 'tags', if applicable
     ```
     - Order of attributes on blocks:
     ```   
     1. 'name' with block name
     2. 'become[_user|_method]', if required
     3. (others not mentioned)
     4. 'vars', if any
     5. 'when', if applicable
     6. 'tags', if applicable
     7. 'block:' statement
     8. 'rescue', if any
     9. 'always', if any
     ```
     - Order of attributes on plays (recommendation, not enforced):
     ```        
     1. 'name' with block name
     2. 'hosts'
     3. 'become[_user|_method]', if required
     4. (others not mentioned)
     5. 'tags', if required
     6. final 'tasks:' statement
     ```

2. ### Parameter variable definition
   - Variables which expose role functionality to the user are called parameter(-variable)s or configuration variables.
   - Parameter variables must be defined in `defaults/main.yml` and be declared with a sensible default value.
   - Every parameter variable must be documented with a comment preceding the variable definition.
   
3. ### Parameter documentation and type hinting
   - Documentation comments start with the variable name it documents, followed by a pydantic-style similar type hint, 
     hinting the variables general type structure.
   - Complex (imaginary) types like 'FilePath' or 'host' can be used only in conjunction with their underlying 
     primitive python type, if it helps clarify the variables purpose. 
     <br>Example:
   ```
    # dhparam_file -> Optional[str|FilePath]: File path of Diffie-Hellmann parameters file.
    dhparam_file: "/etc/ssl/dhparams.pem"
   ```
   - Any special arguments (i.e. keywords for indices) that are supported have to be listed and described.
     <br>Example:
   ```
   # pve_cluster_ha_groups -> list[dict={
   # 'name' -> str: Name of HA group.
   # 'comment' -> str: Comment of HA group.
   # 'nofailback' -> bool: (default=false) Optional, The CRM tries to run services on the node with the highest priority.
   # [...]
   ```
   - Variables which are expected to have specific content are hinted by a complete(!) list of valid values: 
     '`<type>=Selection(<comma separated list of valid values>)`'
     <br>Example:
   ```
   # 'application' -> str=Selection('cephfs', 'rbd', 'rgw'): (default = 'rbd') Optional, The application of the pool.
   # 'hosts' -> list[str]|str='all': (Optional) Hosts where OSD creation is applicable to. 'all' applies to all hosts (same as omitting it).
   ```
   - Numeral values which expect a given range are hinted by '`int`' or '`float`' and 
     '`<type>=range(<min value or '-inf' for no lower bound>,<max value or 'inf' for no upper bound>)`'
     <br>Example:
   ```
   # 'min_size' -> int=range(1, 7): (default = 2) Minimum number of replicas per object
   ```
   - Specific custom values can be hinted by regex, too: '`<type>=regex(<regex>)`'
     <br>Example:
   ```
   # 'target_size' -> str=regex('^(\d+(\.\d+)?)([KMGT])?$'): The estimated target size of the pool for the PG autoscaler.
   ```
   - Mappings, e.g. dicts often expect a specific internal structure with specific attribute names and are hinted as:
     '`dict={<each expected key and value on a new line>}`'
     <br>Example:
   ```
   # pve_ceph_custom_crush_tunables -> list[dict={
   # 'name' -> str: Name of tunable option.
   # 'value' -> int: Value of tunable option.
   # OR
   # <tunable option name> -> str: <tunable option value> -> int: Direct mapping of tunable options.
   # }]: (Declarative) Custom CRUSH tunables.
   ```
   - Because every parameter variable must be defined (=is required), 
     parameter variables without any (sensible) default value are type hinted as "Optional" and
     have `null (null in YAML==None in Python)` as default value. (Note: Optional[\<type>] == Union[\<type>, None].)
     <br>Example:
   ```
   # pve_ssl_certificate -> Optional[str]: (Declarative) Content of HTTPS certificate for PVE WebUI.
   pve_ssl_certificate: null 
   => This variable MUST be defined
   ```
     this stands in contrast to:
   - Variables which are not parameters and not required, must not be type hinted as 'Optional', 
     but documented as such in their description (see below). 
   ```
   # pve_ceph_pools -> list[dict = {
   #   [...]
   #   'quota' -> int: (Optional) (default=0) Pool quota in GibiBytes, 0 disables quota. 
   #    => This variable CAN be defined, but mustn't.
   #   [...]
   # }
   ```
   - For more clarification on 'Optional' as variable type versus optional, as in 'not required', see:
     https://docs.pydantic.dev/2.0/migration/#required-optional-and-nullable-fields
   - Variable type hints are then followed by ': ' and their description consisting of complete english sentences.
   - For parameter variables, the description must start with either:
     - '(Declarative)', marking it as, by their definition itself, reversible impact outcome after role execution, or
     - '(Irreversible)', marking it as, by their definition itself, irreversible impact outcome after role execution. 
     <p>If not sure, use '(Irreversible)'.
   - If a variable can be omitted, and therefore is optional, their description starts with
     the strings '(Optional)' or 'Optional'.
   - If a default value exists, it is documented with '(default=\<default value>)' in the description. 
     The description does not need to contain the optional markers in this case.
   
4. ### Variable naming conventions
   - Variable names are named according to 'snake-case' convention, separating words or abbreviations by '_'.
   - Variable names never contain information about their type or structure. (Structure is documented by comment on declaration.)
   - Parameter variables controlling functionality in this role are always prefixed with 'pve_' in their name.
   - Overwriting parameter variables during runtime will result in troubleshooting issues, therefore transform them to dynamically.
     For identification it might be usefull to maintain the leading 'pve' as '_pve' 
   - Any other variables which are defined dynamically at runtime are prefixed with '_'.
   - Variables which are declared in a 'register' attribute, end in '_raw' or '_reg'.
     If they are looped and therefore contain the 'results' attribute, they must end on 's': '_raws' or '_regs'.
     <br>Example:
     ```      
      ansible.builtin.command: "ceph-volume lvm list {{ item.key }} --format=json"
      register: _ceph_lvm_list_device_raw
     ```
   - Names should always represent an ordered layered logical 'path' in words or abbreviations of <i>what</i> information
     they contain <i>where</i>. On registered command variables, a short version of the command is preferred as variable name (see example above).
     Variable naming examples:
     - A variable which holds information about HA-groups in a cluster is named:
       `pve_cluster_ha_groups`: 'pve' is the prefix, 'cluster' the upper category or abstraction layer (where)
       and 'ha_groups' the content it holds (what).
     - `pve_ceph_cluster_network`: 'pve' = prefix, 'ceph' = logical domain, 'cluster' = logical subdomain in 'ceph', 'network' = variable content.
     - `pve_ceph_pool_force_destroy`: 'pve' = prefix, 'ceph' = logical domain, 'pool' = logical subdomain in 'ceph', 'force_destroy' = configuration information.
     - Logical layers in names are ordered from 'highest' (= most abstract) first to 'lowest' (= most concrete) last. 
     - If names get too long, they should be truncated in the middle, always retaining prefixes 'pve' or '_' and the most concrete last part. 
     - Variables that are declared in a task local scope (i.e. in the `vars:` attribute), don't need to follow specific naming rules other than to be descriptive.

5. ### Task and block naming convention
   Names of blocks and tasks:
   - Are never quoted.
   - Must start with an uppercase word.
   - Represent a correct english imperative sentence .
   - Should not end with dot '.'.
   - Describe in short what the block or task <i>actually does</i>.
   - Should be seen as analog to documentation comments in coding.
   - Do not portrait or contain other tasks, variables, ideas, futures, abstracts, generics, and so on.

6. ### Tags naming convention
   Names of tags:
   - Are never quoted.
   - Are in 'snake-case', separating words or abbreviations by '_'.
   - Represent an ordered layered logical 'path' of the abstract domain it applies to.
   - Have no prefixes or suffixes.
   - Never use pluralized forms(?) # TODO discuss
   - Examples: 
     - `ssh`: Run features managing SSH only.
     - `pve_cluster_ha_group`: Run features managing PVE HA groups only.
     - `ceph_pool_rbd_mirror`: Run features managing Ceph RBD pool mirrors only.
     - `ceph_osd_remove`: Run features which remove OSDs only.
     - `ceph_crush_rules_create`: Run features which create Ceph CRUSH map rules only.

7. ### Task file naming convention
   Names of task files:
   - See tags naming conventions.
   - YAML file endings are abbreviated with `.yml`, not `.yaml`.

8. ### Linting
   - Ansible linting is always required!
   - Only commits without any linting warnings or errors will be accepted.
   - For linting the ansible-lint executable is used.
   - Most linting rules are managed through a '.ansible-lint' file in the repository root directory.
   - Current '.ansible-lint' content:
   ```
   ---
    skip_list:
    - yaml[comments]: Comments don't need to follow intendation. Improves readability and prepares a potential later use of mkdocs.
    - name[missing]: (DEBUG) All tasks must be named, temporarily disabled for better readability when debugging.
    - no-handler: This rule checks for the correct handling of changes to results or conditions. The recommended approach is to use notify and move tasks to handlers.
   ```
