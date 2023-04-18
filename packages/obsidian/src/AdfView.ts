import {
	FileSystemAdapter,
	ItemView,
	Vault,
	Workspace,
	WorkspaceLeaf,
} from "obsidian";
import {
	ConfluenceUploadSettings,
	MdToADF,
	LoaderAdaptor,
} from "@markdown-confluence/lib";
import React from "react";
import ReactDOM from "react-dom";
import { ReactRenderer } from "@atlaskit/renderer";
import { JSONDocNode } from "@atlaskit/editor-json-transformer";
import { traverse } from "@atlaskit/adf-utils/traverse";
import { IntlProvider } from "react-intl-next";

export const ADF_VIEW_TYPE = "AtlassianDocumentFormatView";

export default class AdfView extends ItemView {
	displayText: string;
	settings: ConfluenceUploadSettings.ConfluenceSettings;
	filePath: string | undefined;
	fileName: string;
	vault: Vault;
	workspace: Workspace;
	mdToAdf: MdToADF;
	adaptor: LoaderAdaptor;

	getViewType(): string {
		return ADF_VIEW_TYPE;
	}
	getDisplayText(): string {
		return this.displayText ?? "ADF Preview";
	}

	getIcon() {
		return "dot-network";
	}

	constructor(
		settings: ConfluenceUploadSettings.ConfluenceSettings,
		leaf: WorkspaceLeaf,
		initialFileInfo: { path: string | undefined; basename: string },
		adaptor: LoaderAdaptor
	) {
		super(leaf);
		this.settings = settings;
		this.filePath = initialFileInfo.path;
		this.fileName = initialFileInfo.basename;
		this.vault = this.app.vault;
		this.workspace = this.app.workspace;
		this.mdToAdf = new MdToADF();
		this.adaptor = adaptor;
	}

	async onOpen() {
		const container = this.containerEl.children[1] as HTMLElement;
		container.style.backgroundColor = "#FFFFFF";

		if (!this.filePath) {
			container.textContent = "Current file not supported";
			return;
		}

		const md = await this.adaptor.loadMarkdownFile(this.filePath);
		const adf = this.mdToAdf.convertMDtoADF(md).contents;
		const renderADF = this.convertMediaFilesToLocalPath(adf);

		const locale = "en";
		const messages = {
			// Your localized messages
		};

		const intlProvider = React.createElement(
			IntlProvider,
			{
				locale: locale,
				messages: messages,
			},
			// @ts-ignore
			React.createElement(ReactRenderer, { document: renderADF })
		);

		ReactDOM.render(intlProvider, container);
	}

	convertMediaFilesToLocalPath(adf: JSONDocNode): JSONDocNode {
		return traverse(adf, {
			media: (node, parent) => {
				if (node?.attrs?.type === "file") {
					const currentUrl = node?.attrs?.url as string;
					const test = this.app.vault.adapter as FileSystemAdapter;
					const vaultPath =
						this.app.metadataCache.getFirstLinkpathDest(
							currentUrl.replace("file://", ""),
							this.filePath ?? ""
						);
					if (!vaultPath) {
						return false;
					}
					const path = test.getResourcePath(vaultPath.path);
					node.attrs.type = "external";
					node.attrs.url = path;
					return node;
				}
			},
		}) as JSONDocNode;
	}

	getBasePath() {
		const adapter = app.vault.adapter;
		if (adapter instanceof FileSystemAdapter) {
			return adapter.getBasePath();
		}
		throw new Error("No Path???");
	}

	async onClose() {
		// Nothing to clean up.
	}
}
