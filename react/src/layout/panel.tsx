import { useContext } from "react";
import { interpolate } from "../utility/string";
import { LayoutProps, Layout } from "./layout";
import { useStore } from "react-redux";
import { EditorPanel } from "../component/reusable/panel";
import "./panel.scss";
import React from "react";
import { CSchema, CSimulationInfoPromise } from "../data/appwrapper";
import { SchemaLayout } from "../utility/schema";
import { LAYOUTS } from "./layouts";
import { useShown } from "../hook/shown";

export type PanelConfig = {
    basic: SchemaLayout[],
    advanced: SchemaLayout[],
    title: string,
    shown: string
}

export class PanelLayout extends Layout<PanelConfig, {}> {
    basic?: Layout[];
    advanced?: Layout[];

    constructor(config: PanelConfig) {
        super(config);
        this.basic = (!!config.basic) ? config.basic.map(LAYOUTS.getLayoutForSchema) : undefined;
        this.advanced = (!!config.advanced) ? config.advanced.map(LAYOUTS.getLayoutForSchema) : undefined;
    }

    getFormDependencies = () => {
        return [...(this.basic || []), ...(this.advanced || [])].map(childLayout => childLayout.getFormDependencies()).flat();
    }

    component = (props: LayoutProps<{}>) => {
        let simulationInfoPromise = useContext(CSimulationInfoPromise);
        let schema = useContext(CSchema);

        let shown = useShown(this.config.shown, true, modelsWrapper, ValueSelectors.Models);

        let store = useStore();

        let title = interpolate(this.config.title).withDependencies(modelsWrapper, ValueSelectors.Models).raw();

        let mapLayoutsToComponents = (views: Layout[]) => views.map((child, idx) => {
            let LayoutComponent = child.component;
            return <LayoutComponent key={idx}></LayoutComponent>;
        });

        let mainChildren = (!!this.basic) ? mapLayoutsToComponents(this.basic) : undefined;
        let modalChildren = (!!this.advanced) ? mapLayoutsToComponents(this.advanced) : undefined;

        let submit = () => {
            //formController.saveToModels(store.getState());
            simulationInfoPromise.then(simulationInfo => {
                (modelsWrapper as ModelsWrapper).saveToServer(simulationInfo, Object.keys(schema.models), store.getState());
            })

        }

        let formProps = {
            submit: submit,
            cancel: formController.cancelChanges,
            showButtons: formController.isFormStateDirty(),
            formValid: formController.isFormStateValid(),
            mainChildren,
            modalChildren,
            title: title || this.name,
            id: this.name
        }

        return (
            <>
                {
                    shown && <EditorPanel {...formProps}/>
                }
            </>
            
        )
    }
}
