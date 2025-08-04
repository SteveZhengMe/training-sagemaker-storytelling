from pytablewriter import MarkdownTableWriter


def get_markdown_content(header_list: list, value_list: list) -> str:
    """
    Assume the multiple files are within the Sagemaker Step
    This file does nothing to the data preparation, it uses a 3rd party library
    """
    writer = MarkdownTableWriter(
        table_name="example_table",
        headers=header_list,
        value_matrix=value_list,
    )
    return writer.dumps()
