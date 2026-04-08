def run_pipeline(file_path):

    # 1. load
    image = load_drawing(file_path)

    # 2. preprocess
    data = preprocess(image)

    # 3. init clients
    instructor_client = get_instructor_client()
    tools = create_tools()
    agent = create_agent()

    # 4. graph
    graph = build_graph(agent, tools, instructor_client)

    # 5. run
    result = graph.invoke({
        "messages": [],
        "image_base64": data["image_base64"],
        "ocr_text": data["ocr_text"],
        "context": ""
    })

    return result["final_output"]