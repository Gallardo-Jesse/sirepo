import React, { useContext, useState } from "react";
import { FunctionComponent } from "react";
import { Badge, Button, Modal, Tab, Table, Tabs } from "react-bootstrap";
import { useDispatch, useStore } from "react-redux";
import { formActionFunctions } from "../../component/reusable/form";
import { EditorPanel, Panel, ViewPanelActionButtons } from "../../component/reusable/panel";
import { HandleFactoryWithOverrides } from "../../data/alias";
import { CSchema } from "../../data/appwrapper";
import { getValueSelector, newModelFromSchema, revertDataStructure, StoreTypes } from "../../data/data";
import { Dependency } from "../../data/dependency";
import { CHandleFactory, DataHandle } from "../../data/handle";
import { useCoupledState } from "../../hook/coupling";
import { ArrayFieldElement, ArrayFieldState } from "../../store/common";
import { FormFieldState } from "../../store/formState";
import { ModelState } from "../../store/models";
import { Layout } from "../layout";
import { LAYOUTS } from "../layouts";

type TemplateSettings = {
    type: string,
    name: string,
    modelName: string,
    items: SchemaLayoutJson[]
}

export type MadxBeamlineElementsConfig = {
    elementsDependency: string,
    templateGroups: {
        name: string,
        types: string[]
    }[],
    elementTemplates: TemplateSettings[]
}

function BeamlineNewElementEditor(props: { template: TemplateSettings, onComplete: (modelState: ModelState) => void, name: string, onHide: () => void }) {
    let [layouts, _, updated] = useCoupledState(props.template, () => props.template.items.map((i, idx) => {
        return LAYOUTS.getLayoutForSchema(i);
    }))

    let schema = useContext(CSchema);
    let store = useStore();
    let dispatch = useDispatch();
    let parentHandleFactory = useContext(CHandleFactory);

    let overridesHandleFactory = new HandleFactoryWithOverrides(schema, [
        {
            fake: props.template.modelName,
            value: newModelFromSchema(schema.models[props.template.modelName], { name: props.name }),
            onSave: props.onComplete
        }
    ], parentHandleFactory);

    return (
        <CHandleFactory.Provider value={overridesHandleFactory}>
            <Modal show={props.template !== undefined} onHide={props.onHide}>
                <Modal.Header>
                    {props.template.name}
                </Modal.Header>
                <Modal.Body>
                    {layouts.map((l, idx) => {
                        let Comp = l.component;
                        return <Comp key={idx}/>;
                    })}
                </Modal.Body>
                <ViewPanelActionButtons onSave={() => {
                    overridesHandleFactory.save(store.getState(), dispatch)
                    props.onHide();
                }} onCancel={props.onHide} canSave={overridesHandleFactory.isValid(store.getState())}/>
            </Modal>
        </CHandleFactory.Provider>
    )
}

export class MadxBeamlineElementsLayout extends Layout<MadxBeamlineElementsConfig, {}> {
    constructor(config: MadxBeamlineElementsConfig) {
        super(config);
    }

    component: FunctionComponent<{ [key: string]: any; }> = (props) => {
        let handleFactory = useContext(CHandleFactory);
        //let activeBeamlineId = handleFactory.createHandle(new Dependency(this.config.activeBeamlineDependency), StoreTypes.Models).hook().value;
        let elementsHandle = handleFactory.createHandle(new Dependency(this.config.elementsDependency), StoreTypes.FormState).hook();
        let elementsValue = revertDataStructure(elementsHandle.value, getValueSelector(StoreTypes.FormState)) as ArrayFieldState<ModelState>;

        let [newElementModalShown, updateNewElementModalShown] = useState(false);
        let [shownModalTemplate, updateShownModalTemplate] = useState<TemplateSettings>(undefined);
        let defaultGroup = this.config.templateGroups?.length > 0 ? this.config.templateGroups[0].name : undefined;

        let uniqueNameForType = (type: string) => {
            let maxId = elementsValue.filter(e => e.model.charAt(0) === type.charAt(0)).reduce<number>((prev: number, cur: ArrayFieldElement<ModelState>, idx) => {
                let numberPart = (/.*?(\d*).*?/g).exec(cur.item.name as string)[1];
                return Math.max(prev, parseInt(numberPart.length > 0 ? numberPart : "0"))
            }, 1);
            return `${type.charAt(0)}${maxId + 1}`
        }

        let getTemplateSettingsByType = (type: string) => {
            let ret = this.config.elementTemplates.find(t => {
                return t.type == type
            });
            if(!ret) {
                throw new Error(`could not find template settings for type=${type}, ${JSON.stringify(this.config.elementTemplates)}`)
            }
            return ret;
        }

        let addBeamlineElement = (template: TemplateSettings, modelValue: ModelState) => {
            console.log(`adding beamline element with type=${template.type}`, modelValue);
        }

        return (
            <>
                <Modal show={newElementModalShown} onHide={() => updateNewElementModalShown(false)}>
                    <Modal.Header>
                        New Beamline Element
                    </Modal.Header>
                    <Modal.Body>
                        <Tabs defaultActiveKey={defaultGroup}>
                            {
                                this.config.templateGroups?.map(tg => {
                                    return (
                                        <Tab eventKey={tg.name} title={tg.name} key={tg.name}>
                                            {
                                                ([...new Set(tg.types)].sort((a,b) => a.localeCompare(b))).map(t => {
                                                    let s = getTemplateSettingsByType(t);
                                                    return (    
                                                        <Button key={`${t}`} variant="outline-secondary" onClick={() => {
                                                            updateShownModalTemplate(s)
                                                        }}>
                                                            {s.name}
                                                        </Button>
                                                    )
                                                })
                                            }
                                        </Tab>
                                    )
                                })
                            }
                        </Tabs>
                    </Modal.Body>
                </Modal>
                {
                    shownModalTemplate && (
                        <BeamlineNewElementEditor name={uniqueNameForType(shownModalTemplate.type)} onHide={() => updateShownModalTemplate(undefined)} template={shownModalTemplate} onComplete={(mv) => addBeamlineElement(shownModalTemplate, mv)}/>
                    )
                }
                <Panel title="Beamline Elements" panelBodyShown={true}>
                    <div className="d-flex flex-column">
                        <div className="d-flex flex-row flew-nowrap justify-content-right">
                            <Button variant="primary" size="sm" onClick={() => updateNewElementModalShown(true)}>New Element</Button>
                        </div>
                        <Table>
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Description</th>
                                    <th>Length</th>
                                    <th>Bend</th>
                                </tr>
                            </thead>
                            {
                                [...new Set(elementsValue.map((ev: ArrayFieldElement<ModelState>) => ev.model))].sort((a: string, b: string) => a.localeCompare(b)).map((category: string) => {
                                    return (
                                        <tbody key={category}>
                                            <tr>
                                                <td>
                                                    <span>
                                                        {category}
                                                    </span>
                                                </td>
                                            </tr>
                                            {
                                                elementsValue.filter(ev => ev.model == category).map((ev: ArrayFieldElement<ModelState>) => {
                                                    return (
                                                        <React.Fragment key={`${ev.item._id}`}>
                                                            <tr>
                                                                <td>
                                                                    <h6>
                                                                        <Badge bg="secondary">
                                                                            {ev.item.name as string}
                                                                        </Badge>
                                                                    </h6>
                                                                </td>
                                                                <td>
                                                                    {/*??? TODO: garsuga: where does description come from*/}
                                                                </td>
                                                                <td>
                                                                    {ev.item.l !== undefined ? `${(ev.item.l as number).toPrecision(4)}m` : ""}
                                                                </td>
                                                                <td>
                                                                    {ev.item.angle !== undefined ? (ev.item.angle as number).toPrecision(3) : ""}
                                                                </td>
                                                            </tr>
                                                        </React.Fragment>
                                                        
                                                    )
                                                })
                                            }
                                        </tbody>
                                    )
                                    
                                })
                            }
                        </Table>
                    </div>
                </Panel>
            </>
            
        )
    }
}
