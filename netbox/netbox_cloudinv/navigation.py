from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem


def _item(name, text):
    return PluginMenuItem(
        link=f"plugins:netbox_cloudinv:{name}_list",
        link_text=text,
        buttons=(
            PluginMenuButton(
                link=f"plugins:netbox_cloudinv:{name}_add",
                title="추가", icon_class="mdi mdi-plus-thick",
            ),
            PluginMenuButton(
                link=f"plugins:netbox_cloudinv:{name}_import",
                title="일괄 등록", icon_class="mdi mdi-upload",
            ),
        ),
    )


menu = PluginMenu(
    label="클라우드 자원",
    groups=(
        ("대장", (_item("cloudresource", "자원"),)),
        ("기준 정보", (
            _item("cloudplatform", "플랫폼"),
            _item("cloudservice", "서비스"),
        )),
    ),
    icon_class="mdi mdi-cloud-outline",
)
