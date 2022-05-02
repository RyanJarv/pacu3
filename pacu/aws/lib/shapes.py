import botocore.session

from pacu.aws.lib.boto import services, get_model


sess = botocore.session.get_session()

def shapes():
    for svc in services():
        ver = sess.get_config_variable('api_versions').get(svc, None)
        svc_model = sess.get_service_model(svc, api_version=ver)

        # TODO: We can actually just get these directly from sess.get_data
        for name in svc_model.shape_names:
            yield svc_model.shape_for(name)
