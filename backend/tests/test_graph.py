from app.models import Activity, Entity
from app.provenance_graph import ProvenanceGraph
from app.workflow_management import create_activity, create_entity, post_run


def create_provenance_data():
    """创建溯源数据"""
    lv0, att, orb, mkf = (
        create_entity("lv0"),
        create_entity("att"),
        create_entity("orb"),
        create_entity("mkf"),
    )
    obs = create_activity("obs", informers=[], inputs=[lv0])
    post_run(obs, [att, orb, mkf])

    # lv1
    lv1 = create_entity("lv1")
    data_generation_software = create_activity(
        "Data Generation Software", informers=[obs], inputs=[lv0, att, orb, mkf]
    )
    post_run(data_generation_software, [lv1])

    # lv2
    cleaned_events = create_entity("Cleaned Events")
    caldb = create_entity("caldb")
    data_screen_software = create_activity(
        "Data Screen Software", informers=[data_generation_software], inputs=[caldb]
    )
    post_run(data_screen_software, [cleaned_events])

    # lv3
    img, cat, lc, spec = (
        create_entity("Image"),
        create_entity("Catalog"),
        create_entity("Light Curve"),
        create_entity("Spectrum"),
    )
    data_analysis_software = create_activity(
        "Data Analysis Software",
        informers=[data_screen_software],
        inputs=[cleaned_events],
    )
    post_run(data_analysis_software, [img, cat, lc, spec])


def test_nodes(app_context):
    create_provenance_data()
    img = Entity.query.filter_by(name="Image").first()
    das = "Data Analysis Software"
    graph = ProvenanceGraph()
    graph.build_graph(img)
    assert das in [node.name for node in graph.nodes.values()]
