from netbox.plugins import PluginMenu, PluginMenuItem

securitylist = PluginMenuItem(
    link="plugins:netbox_oci:securitylist_list",
    link_text="보안목록",
)
securityrule = PluginMenuItem(
    link="plugins:netbox_oci:securityrule_list",
    link_text="보안규칙",
)

menu = PluginMenu(
    label="OCI",
    groups=(("보안", (securitylist, securityrule)),),
    icon_class="mdi mdi-cloud-outline",
)
