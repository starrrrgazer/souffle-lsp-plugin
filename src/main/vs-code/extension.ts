import path = require("path");
import * as vscode from "vscode";
import * as fs from "fs";

import {
  LanguageClientOptions,
  RevealOutputChannelOn,
} from "vscode-languageclient";

import {
  LanguageClient,
  ServerOptions,
  State,
} from "vscode-languageclient/node";

const outputChannel = vscode.window.createOutputChannel("Souffle LSP");
const LS_LAUNCHER_MAIN: string = "SouffleLanguageServerLauncher";

export class SouffleExtension {
  private languageClient?: LanguageClient;
  private context?: vscode.ExtensionContext;

  setContext(context: vscode.ExtensionContext) {
    this.context = context;
  }

  async init(): Promise<void> {
    try {
      //Server options. LS client will use these options to start the LS.
      let serverOptions: ServerOptions = getServerOptions();

      //creating the language client.
      let clientId = "souffle-vscode-lsclient";
      let clientName = "Souffle LS Client";
      let clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: "file", language: "souffle" }],
        outputChannel: outputChannel,
        revealOutputChannelOn: RevealOutputChannelOn.Never,
      };
      this.languageClient = new LanguageClient(
        clientId,
        clientName,
        serverOptions,
        clientOptions
      );
      
      const disposeDidChange = this.languageClient.onDidChangeState(
        (stateChangeEvent) => {
          if (stateChangeEvent.newState === State.Stopped) {
            vscode.window.showErrorMessage(
              "Failed to initialize the extension"
            );
          } else if (stateChangeEvent.newState === State.Running) {
            vscode.window.showInformationMessage(
              "Extension initialized successfully!"
            );
          }
        }
      );

      let disposable = this.languageClient.start();
      this.languageClient.onReady().then(() => {
        disposeDidChange.dispose();
        this.context!.subscriptions.push(disposable);
      });
    } catch (exception) {
      return Promise.reject("Extension error!");
    }
  }
}

//Create a command to be run to start the LS java process.
function getServerOptions() {
  //Change the project home accordingly.
  const PROJECT_HOME = path.resolve(__dirname, "../");
  const LS_LIB_CONFIG = vscode.workspace.getConfiguration().get("PATH_LSP");
  
  //only for linux
  // let LS_LIB = "build/libs/*";
  // if (LS_LIB_CONFIG) {
  //   LS_LIB = String(LS_LIB_CONFIG);
  // }
  // const LS_HOME = path.join(PROJECT_HOME, LS_LIB);
  // const JAVA_HOME = vscode.workspace.getConfiguration().get("JAVA_HOME");

  // let executable: string = path.join(String(JAVA_HOME), "bin", "java");
  // let args: string[] = ["-cp", LS_HOME];
  // console.log("LS HOME : " + LS_HOME)


  // let classpath: string;
  // if (LS_LIB_CONFIG) {
  //   classpath = String(LS_LIB_CONFIG);
  // } else {
  //   // 默认：枚举 build/libs 下所有 jar
  //   const libsDir = path.join(PROJECT_HOME, "build", "libs");
  //   const jars = fs.readdirSync(libsDir).filter(f => f.endsWith(".jar"));
  //   if (process.platform === "win32") {
  //     classpath = jars.map(j => path.join(libsDir, j)).join(";");
  //   } else {
  //     classpath = jars.map(j => path.join(libsDir, j)).join(":");
  //   }
  // }

  // // JAVA_HOME
  // const JAVA_HOME = vscode.workspace.getConfiguration().get("JAVA_HOME") || process.env.JAVA_HOME;
  // let executable = "java"; // 默认用 PATH 里的 java
  // if (JAVA_HOME) {
  //   executable = path.join(String(JAVA_HOME), "bin", "java");
  // }
  // const args: string[] = ["-cp", classpath, LS_LAUNCHER_MAIN];
  // console.log("executable : " + executable);
  // let serverOptions: ServerOptions = {
  //   command: executable,
  //   args,
  //   options: {env: process.env},
  // };
  // console.log("severOptions : " + serverOptions.args);
  let jarPath: string = path.join(PROJECT_HOME, "build","libs", "Souffle_Ide_Plugin-1.0-SNAPSHOT.jar");
  console.log(jarPath);
  const serverOptions: ServerOptions = {
  command: "java",
  args: ["-jar", jarPath],
};
  return serverOptions;
}

export const extensionInstance = new SouffleExtension();
