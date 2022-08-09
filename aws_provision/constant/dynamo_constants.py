# class DepFlowBuilderBatchStatus:
#     table_name: "dep_flowbuilder_batch_status"
#     part_key: "batch_id"


# class DepEMR:
#     table_name: "dep_emr"
#     part_key: "cluster_id"


# class DepPreprocessorFileClassification:
#     table_name: "dep_preprocessor_file_classification"
#     part_key: "id"


# class DepPreprocessorFileClassificationStatus:
#     table_name: "dep_preprocessor_file_classification_status"
#     part_key: "id"


# class DepFlowBuilderJob:
#     table_name: "dep_flowbuilder_job"
#     part_key: "client"


# class DepFlowBuilderJobInput:
#     table_name: "dep_flowbuilder_job_input"
#     part_key: "job"


# class DepFlowBuilderJobStatus:
#     table_name: "dep_flowbuilder_job_status"
#     part_key: "batch_id"


# class DepFlowBuilderJobStepStatus:
#     table_name: "dep_flowbuilder_job_step_status"
#     part_key: "batch_id"


# class FlowBuilderBatchStatus:
#     table_name: "dep_flowbuilder_batch_status"
#     part_key: "batch_id"


# class DEPFlowBuilderMeta:
#     table_name: "dep_meta"
#     part_key: "client"


# class DepStreamMetadata:
#     table_name: "dep_stream_metadata"
#     part_key: "stream_name"


# class DepStreamStatus:
#     table_name: "dep_stream_status"
#     part_key: "stream_name"


# class DepRuleEngineAudit:
#     table_name: "rule_engine_audit_table"
#     part_key: "id"


# class DepRuleEngineJob:
#     table_name: "rule_engine_job"
#     part_key: "id"


# class DepRuleEngineMetaData:
#     table_name: "rule_engine_metadata"
#     part_key: "id"


# class DepRuleEngineResourceManagement:
#     table_name: "rule_resource_management"
#     part_key: "cluster_id"


# class DepInstanceMapping:
#     table_name: "dep_instance_mapping"
#     part_key: "instance_id"
DepFlowBuilderBatchStatus = {
    "table_name": "dep_flowbuilder_batch_status",
    "part_key": "batch_id"
    }


DepEMR = {
    "table_name": "dep_emr",
    "part_key": "cluster_id"
}

DepPreprocessorFileClassification = {
"table_name": "dep_preprocessor_file_classification",
"part_key": "id"
}


DepPreprocessorFileClassificationStatus ={
"table_name": "dep_preprocessor_file_classification_status",
"part_key": "id"
}


DepFlowBuilderJobName= {
"table_name": "dep_flowbuilder_job_name",
"part_key": "client"
}

DepFlowBuilderJobInput = {
"table_name": "dep_flowbuilder_job_input",
"part_key": "job"
}

DepFlowBuilderJobStatus = {
"table_name": "dep_flowbuilder_job_status",
"part_key": "batch_id"
}


DepFlowBuilderJobStepStatus = {
"table_name": "dep_flowbuilder_job_step_status",
"part_key": "batch_id"
}


FlowBuilderBatchStatus = {
"table_name": "dep_flowbuilder_batch_status",
"part_key": "batch_id"
}

DEPFlowBuilderMeta = {
"table_name": "dep_flowbuilder_metadata",
"part_key": "client"
}


DepStreamMetadata ={
"table_name": "dep_stream_metadata",
"part_key": "stream_name"
}

DepStreamStatus={
"table_name": "dep_stream_status",
"part_key": "stream_name"
}

DepRuleEngineAudit = {
"table_name": "dep_rule_engine_audit_table",
"part_key": "id"
}

DepRuleEngineJob = {
"table_name": "dep_rule_engine_job_name",
"part_key": "id"
}

DepRuleEngineMetaData = {
"table_name": "dep_rule_engine_metadata",
"part_key": "id"
}


DepRuleEngineResourceManagement = {
"table_name": "dep_rule_engine_resource_management",
"part_key": "cluster_id"
}

DepEMRInstanceMapping = {
"table_name": "dep_emr_instance_mapping",
"part_key": "instance_id"
}