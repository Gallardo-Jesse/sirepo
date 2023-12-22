'use strict';

var srlog = SIREPO.srlog;
var srdbg = SIREPO.srdbg;

SIREPO.app.config(() => {
    SIREPO.appReportTypes = `
        <div data-ng-switch-when="buttons" data-buttons-report="" class="sr-plot" data-model-name="{{ modelKey }}" data-report-id="reportId"></div>
        <div data-ng-switch-when="icons" data-icons-report="" class="sr-plot" data-model-name="{{ modelKey }}" data-report-id="reportId"></div>
    `;
});

SIREPO.app.controller('MyAppGuiController', function (appState, panelState, $scope) {
    var self = this;
});


SIREPO.app.controller('MyAppSourceController', function (appState, panelState, $scope) {
    var self = this;

    function handleDogDisposition() {
        panelState.showField('dog', 'favoriteTreat', appState.models.dog.disposition == 'friendly');
    }

    appState.whenModelsLoaded($scope, function() {
        // after the model data is available, hide/show the
        // favoriteTreat field depending on the disposition
        handleDogDisposition();
        appState.watchModelFields($scope, ['dog.disposition'], function() {
            // respond to changes in the disposition field value
            handleDogDisposition();
        });
    });
});

SIREPO.app.directive('appFooter', function() {
    return {
        restrict: 'A',
        scope: {
            nav: '=appFooter',
        },
        template: `
            <div data-common-footer="nav"></div>
        `,
    };
});

SIREPO.app.directive('appHeader', function(appState, panelState) {
    return {
        restrict: 'A',
        scope: {
            nav: '=appHeader',
        },
        template: `
            <div data-app-header-brand="nav"></div>
            <div data-app-header-left="nav"></div>
            <div data-app-header-right="nav">
              <app-header-right-sim-loaded>
                <div data-sim-sections="">
                  <li class="sim-section" data-ng-class="{active: nav.isActive('source')}"><a href data-ng-click="nav.openSection('source')"><span class="glyphicon glyphicon-flash"></span> Source</a></li>
                  <li class="sim-section" data-ng-class="{active: nav.isActive('gui')}"><a href data-ng-click="nav.openSection('gui')"><span class="glyphicon glyphicon-education"></span> GUI Demo</a></li>
                </div>
              </app-header-right-sim-loaded>
              <app-settings>
              </app-settings>
              <app-header-right-sim-list>
              </app-header-right-sim-list>
            </div>
        `,
    };
});

SIREPO.app.directive('buttonsReport', function(appState) {
    return {
        restrict: 'A',
        scope: {
        },
        template: `
            <div class="row">
                <div class="col col-md-6">
                    <div style="padding: 8px 4px;"><label>Action Buttons</label><span data-sr-tooltip="Proposed class change from btn-info to btn-primary"></span></div>
                    <div>Current</div>
                    <span style="padding: 8px 4px;"><button class="btn btn-info btn-xs" title="move up"><span class="glyphicon glyphicon-arrow-up"></span></button></span>
                    <span style="padding: 8px 4px;"><button class="btn btn-info btn-xs" title="move down"><span class="glyphicon glyphicon-arrow-down"></span></button></span>
                    <span style="padding: 8px 4px;"><button class="btn btn-info btn-xs" title="copy"><span class="glyphicon glyphicon-duplicate"></span></button></span>
                    <span style="padding: 8px 4px;"><button class="btn btn-info btn-xs" title="edit"><span class="glyphicon glyphicon-pencil"></span></button></span>
                    <span style="padding: 8px 4px;"><button class="btn btn-danger btn-xs" title="delete"><span class="glyphicon glyphicon-remove"></span></button></span>
                    <div>Proposed</div>
                    <span style="padding: 8px 4px;"><button class="btn btn-primary btn-xs" title="Move up"><span class="glyphicon glyphicon-arrow-up"></span></button></span>
                    <span style="padding: 8px 4px;"><button class="btn btn-primary btn-xs" title="Move down"><span class="glyphicon glyphicon-arrow-down"></span></button></span>
                    <span style="padding: 8px 4px;"><button class="btn btn-primary btn-xs" title="Copy"><span class="glyphicon glyphicon-duplicate"></span></button></span>
                    <span style="padding: 8px 4px;"><button class="btn btn-primary btn-xs" title="Edit"><span class="glyphicon glyphicon-pencil"></span></button></span>
                    <span style="padding: 8px 4px;"><button class="btn btn-danger btn-xs" title="Delete"><span class="glyphicon glyphicon-remove"></span></button></span>
                </div>
                <div class="col col-md-6">
                    <div style="padding: 8px 8px;"><label>Dialog Buttons</label><span data-sr-tooltip="Proposed text change from 'Save Changes' to 'Save'"></span></div>
                    <div>Current</div>
                    <button class="btn btn-primary">Save Changes</button>
                    <button class="btn btn-default">Cancel</button>
                    <div>Proposed</div>
                    <button class="btn btn-primary" title="Save">Save</button>
                    <button class="btn btn-default" title="Cancel">Cancel</button>
                </div>
            </div>
            <div class="row">
                <div class="col col-md-6">
                    <div style="padding: 8px 8px;"><label>Boolean Button</label><span data-sr-tooltip="Proposed change to checkboxes from bootstrap"></span></div>
                    <div>Current</div>
                    <div data-field-editor="'bool'" data-model-name="'buttonsReport'" data-model="buttonsReport"></div>
                    <div>Proposed</div>
                    <!--
                    <div>
                        <label>No</label>
                        <div style="display: inline-block;">
                            <input data-size="small" class="sr-bs-toggle" data-ng-model="buttonsReport" data-bootstrap-toggle="" data-model="buttonsReport" data-field="'bool'" data-info="booInfo" data-field-delegate="boolDelegate" type="checkbox"><span class="toggle-handle btn btn-default">
                            <label>Yes</label>
                        </div>
                    -->
                    <div>TBD</div>
                </div>
                <div class="col col-md-6">
                    <div style="padding: 8px 8px;"><label>Checkbox Group</label><span data-sr-tooltip="Proposed change to grouped checkboxes from glyphicons"></span></div>
                    <div>Current</div>
                    <div>All <span class="glyphicon" data-ng-class="checkboxGroup.all ? 'glyphicon-check' : 'glyphicon-unchecked'" data-ng-model="checkboxGroup.all" data-ng-click="toggleAll()"></span> One <span class="glyphicon" data-ng-class="checkboxGroup.one ? 'glyphicon-check' : 'glyphicon-unchecked'" data-ng-model="checkboxGroup.one" data-ng-click="toggleCheck('one')"></span> Two <span class="glyphicon"  data-ng-class="checkboxGroup.two ? 'glyphicon-check' : 'glyphicon-unchecked'" data-ng-model="checkboxGroup.two" data-ng-click="toggleCheck('two')"></span></div>
                    <div>Proposed</div>
                    <div>All <input id="all_new" type="checkbox" data-ng-model="group" data-ng-click="toggleAll()" style="accent-color: #337ab7;"> One <input type="checkbox" data-ng-model="checkboxGroup.one" data-ng-click="toggleCheck('one')" style="accent-color: #337ab7;"> Two <input type="checkbox" data-ng-model="checkboxGroup.two" data-ng-click="toggleCheck('two')" style="accent-color: #337ab7;"></div>
                </div>
            </div>
        `,
        controller: function($scope, $element) {
            $scope.buttonsReport = appState.models.buttonsReport;
            $scope.booInfo = appState.modelInfo('buttonsReport', 'bool').bool;
            $scope.boolDelegate = () => {};
            $scope.group = true;
            $scope.checkboxGroup = {
                one: true,
                two: true,
            };
        

            $scope.toggleAll = () => {
                $scope.group = ! $scope.group;
                for (const name in $scope.checkboxGroup) {
                    $scope.checkboxGroup[name] = $scope.group;
                }
            };

            $scope.toggleCheck = name => {
                $scope.checkboxGroup[name] = ! $scope.checkboxGroup[name];
                const vals = Object.values($scope.checkboxGroup);
                let v =  vals[0];
                let indeterminate = false;
                for (let i = 0; i < vals.length; ++i) {
                    indeterminate = vals[i] !== v;
                    if (indeterminate) {
                        break;
                    }
                    v = vals[i];
                }
                $($element).find('input#all_new')[0].indeterminate = indeterminate;
                if (! indeterminate) {
                    $scope.group = $scope.checkboxGroup[name];
                }
            };
        },
    };
});


SIREPO.app.directive('iconsReport', function() {
    return {
        restrict: 'A',
        scope: {
        },
        template: `
            <div class="row">
                <div class="col col-md-12">
                    <div data-ng-repeat="group in iconGroups track by group.name" style="padding: 8px 8px;"><label>{{ group.title }} Icons</label>
                        <table class="table table-striped table-condensed radia-table-dialog">
                            <thead>
                                <th>{{ group.title }}</th>
                                <th>Icon</th>
                                <th>Color</th>
                                <th>Code</th>
                            </thead>
                            <tbody>
                                <tr data-ng-repeat="item in group.icons track by $index">
                                    <td>{{ item.title }}</td>
                                    <td><span class="glyphicon glyphicon-{{ item.glyphicon }} {{ item.classes }}" style="padding: 8px 8px; color:{{ item.color }};" title="{{ item.title }}"></span></td>
                                    <td>{{ item.color || 'Default' }}</td>
                                    <td data-ng-click="copyCode(group, item)" style="cursor:copy;"><code id="{{ codeId(group, item) }}">&lt;span class="glyphicon glyphicon-{{ item.glyphicon }} {{ item.classes }}" title="{{ item.title }}"&gt;&lt;/span&gt;</code></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
            </div>
        `,
        controller: function($scope, $element) {
            $scope.iconGroups = [
                {
                    name: 'status',
                    title: 'Status',
                    icons: [
                        {
                            type: 'canceled',
                            title: 'Canceled',
                            glyphicon: 'ban-circle',
                        },
                        {
                            type: 'completed', 
                            title: 'Completed',
                            glyphicon: 'ok-circle',
                            color: 'green',
                        },
                        {
                            type: 'error',
                            title: 'Error',
                            glyphicon: 'remove',
                            color: 'red',
                        },
                        {
                            type: 'missing',
                            title: 'Missing',
                            glyphicon: 'question-sign',
                        },
                        {
                            type: 'none',
                            title: 'None / Not Started',
                            glyphicon: 'minus',
                        },
                        {
                            type: 'pending',
                            title: 'Pending',
                            glyphicon: 'hourglass',
                        },
                        {
                            type: 'running',
                            title: 'Running',
                            glyphicon: 'refresh',
                            classes: 'running-icon',
                        },
                    ],
                },
                {
                    name: 'header',
                    title: 'Header',
                    icons: [
                        {
                            type: 'sims',
                            title: 'Simulations',
                            glyphicon: 'th-list',
                        },
                        {
                            type: 'new-sim', 
                            title: 'New Simulation',
                            glyphicon: 'file',
                        },
                        {
                            type: 'new-folder',
                            title: 'New Folder',
                            glyphicon: 'folder-close',
                        },
                        {
                            type: 'help',
                            title: 'Help',
                            glyphicon: 'question-sign',
                        },
                        {
                            type: 'source',
                            title: 'Source Tab',
                            glyphicon: 'flash',
                        },
                        {
                            type: 'visualization',
                            title: 'Visualization Tab',
                            glyphicon: 'picture',
                        },
                    ],
                },
            ];

            $scope.codeId = (group, item) => `code-${group.name}-${item.type}`;

            $scope.copyCode = (group, item) => {
                navigator.clipboard.writeText(
                    $($element).find(`code#${$scope.codeId(group, item)}`).text()
                );
            };
        },
    };
});