import { useEffect, useState } from "react";
import {
  DOCUMENT_TYPES,
  GOV_DOC_TYPES,
  INTEREST_OPTIONS,
  PROFILE_STEPS,
  buildPayload,
  defaultProfile,
  emptyAddress,
} from "../../constants/employeeProfile";
import DragDropUpload from "../../components/DragDropUpload";
import { IMAGE_ACCEPT } from "../../constants/uploadConfig";
import { Field, Input, Select, TextArea } from "./FormField";

function setNested(setForm, path, value) {
  setForm((prev) => {
    const next = { ...prev };
    let cur = next;
    for (let i = 0; i < path.length - 1; i++) {
      cur[path[i]] = Array.isArray(cur[path[i]]) ? [...cur[path[i]]] : { ...cur[path[i]] };
      cur = cur[path[i]];
    }
    cur[path[path.length - 1]] = value;
    return next;
  });
}

export default function EmployeeProfileForm({ initial, isEdit, onSubmit, submitting }) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState(initial || defaultProfile());

  useEffect(() => {
    if (initial) setForm(initial);
  }, [initial]);

  const update = (key, value) => setForm((p) => ({ ...p, [key]: value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(buildPayload(form, isEdit), form.pendingFiles || {});
  };

  const renderEmployment = () => (
    <div className="grid md:grid-cols-2 gap-4">
      <Field label="Employee ID"><Input value={form.employee_id} onChange={(e) => update("employee_id", e.target.value)} /></Field>
      <Field label="Employee Code"><Input value={form.employee_code} onChange={(e) => update("employee_code", e.target.value)} placeholder="Auto-generated if empty" /></Field>
      <Field label="Designation *"><Input required value={form.designation} onChange={(e) => update("designation", e.target.value)} /></Field>
      <Field label="Department *"><Input required value={form.department} onChange={(e) => update("department", e.target.value)} /></Field>
      <Field label="Work Location"><Input value={form.work_location} onChange={(e) => update("work_location", e.target.value)} placeholder="e.g. Bangalore Office" /></Field>
      <Field label="Date of Joining *"><Input required type="date" value={form.joining_date} onChange={(e) => update("joining_date", e.target.value)} /></Field>
      <Field label="Employment Type"><Select value={form.employment_type} onChange={(e) => update("employment_type", e.target.value)}><option value="full-time">Full-time</option><option value="part-time">Part-time</option><option value="contract">Contract</option><option value="intern">Intern</option></Select></Field>
      <Field label="Reporting Manager"><Input value={form.reporting_manager} onChange={(e) => update("reporting_manager", e.target.value)} /></Field>
      <Field label="Project Lead"><Input value={form.project_lead} onChange={(e) => update("project_lead", e.target.value)} /></Field>
      <Field label="Tech Owner"><Input value={form.tech_owner} onChange={(e) => update("tech_owner", e.target.value)} /></Field>
      <Field label="Company Email *"><Input required type="email" value={form.company_email} onChange={(e) => update("company_email", e.target.value)} /></Field>
      <Field label="Employment Status"><Select value={form.employment_status} onChange={(e) => update("employment_status", e.target.value)}><option value="active">Active</option><option value="inactive">Inactive</option><option value="on-leave">On Leave</option><option value="terminated">Terminated</option></Select></Field>
      {!isEdit && (
        <Field label="Login Password *"><Input required type="password" value={form.password} onChange={(e) => update("password", e.target.value)} /></Field>
      )}
      {isEdit && (
        <Field label="Reset Password"><Input type="password" value={form.password} onChange={(e) => update("password", e.target.value)} placeholder="Leave blank to keep current" /></Field>
      )}
    </div>
  );

  const renderPersonal = () => (
    <div className="grid md:grid-cols-2 gap-4">
      <Field label="Title"><Select value={form.title} onChange={(e) => update("title", e.target.value)}><option value="">Select</option><option>Mr</option><option>Mrs</option><option>Ms</option><option>Dr</option></Select></Field>
      <Field label="First Name *"><Input required value={form.first_name} onChange={(e) => update("first_name", e.target.value)} /></Field>
      <Field label="Middle Name"><Input value={form.middle_name} onChange={(e) => update("middle_name", e.target.value)} /></Field>
      <Field label="Last Name *"><Input required value={form.last_name} onChange={(e) => update("last_name", e.target.value)} /></Field>
      <Field label="Gender"><Select value={form.gender} onChange={(e) => update("gender", e.target.value)}><option value="">Select</option><option>Male</option><option>Female</option><option>Other</option></Select></Field>
      <Field label="Father Name"><Input value={form.father_name} onChange={(e) => update("father_name", e.target.value)} /></Field>
      <Field label="Date of Birth"><Input type="date" value={form.date_of_birth} onChange={(e) => update("date_of_birth", e.target.value)} /></Field>
      <Field label="Nationality"><Input value={form.nationality} onChange={(e) => update("nationality", e.target.value)} /></Field>
      <Field label="Marital Status"><Input value={form.marital_status} onChange={(e) => update("marital_status", e.target.value)} /></Field>
      <Field label="Anniversary Date"><Input type="date" value={form.anniversary_date} onChange={(e) => update("anniversary_date", e.target.value)} /></Field>
      <Field label="Number of Children"><Input type="number" min="0" value={form.number_of_children} onChange={(e) => update("number_of_children", e.target.value)} /></Field>
      <Field label="Blood Group"><Input value={form.blood_group} onChange={(e) => update("blood_group", e.target.value)} /></Field>
      <Field label="Passport Photo">
        <DragDropUpload
          compact
          accept={IMAGE_ACCEPT}
          value={form.pendingFiles?.profile_photo || null}
          onChange={(file) => update("pendingFiles", { ...form.pendingFiles, profile_photo: file })}
          hint="PNG or JPG, max 10 MB"
        />
      </Field>
    </div>
  );

  const renderGov = () => (
    <div className="space-y-4">
      <div className="grid md:grid-cols-2 gap-4">
        <Field label="PAN Number"><Input value={form.pan_number} onChange={(e) => update("pan_number", e.target.value)} /></Field>
        <Field label="UAN Number"><Input value={form.uan_number} onChange={(e) => update("uan_number", e.target.value)} /></Field>
        <Field label="PF Number"><Input value={form.pf_number} onChange={(e) => update("pf_number", e.target.value)} /></Field>
        <Field label="Aadhaar Number"><Input value={form.aadhaar_number} onChange={(e) => update("aadhaar_number", e.target.value)} /></Field>
        <Field label="Passport Number"><Input value={form.passport_number} onChange={(e) => update("passport_number", e.target.value)} /></Field>
        <Field label="Passport Issue Date"><Input type="date" value={form.passport_issue_date} onChange={(e) => update("passport_issue_date", e.target.value)} /></Field>
        <Field label="Passport Expiry Date"><Input type="date" value={form.passport_expiry_date} onChange={(e) => update("passport_expiry_date", e.target.value)} /></Field>
        <Field label="Passport Issue Place"><Input value={form.passport_issue_place} onChange={(e) => update("passport_issue_place", e.target.value)} /></Field>
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        {GOV_DOC_TYPES.map((d) => (
          <Field key={d.key} label={d.label}>
            <DragDropUpload
              compact
              value={form.pendingFiles?.[d.key] || null}
              onChange={(file) => update("pendingFiles", { ...form.pendingFiles, [d.key]: file })}
            />
          </Field>
        ))}
      </div>
    </div>
  );

  const renderAddressBlock = (type, label) => {
    const key = type === "permanent" ? "permanent_address" : "correspondence_address";
    const addr = form[key];
    return (
      <div className="border rounded-lg p-4">
        <h4 className="font-medium mb-3">{label}</h4>
        <div className="grid md:grid-cols-2 gap-3">
          {["address_line_1", "address_line_2", "city", "state", "country", "pin_code"].map((f) => (
            <Field key={f} label={f.replaceAll("_", " ")}>
              <Input
                value={addr[f] || ""}
                onChange={(e) => setForm((p) => ({ ...p, [key]: { ...p[key], [f]: e.target.value } }))}
              />
            </Field>
          ))}
        </div>
      </div>
    );
  };

  const renderAddress = () => (
    <div className="space-y-4">
      {renderAddressBlock("permanent", "Permanent Address")}
      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={form.same_as_permanent}
          onChange={(e) => {
            const checked = e.target.checked;
            setForm((p) => ({
              ...p,
              same_as_permanent: checked,
              correspondence_address: checked ? { ...p.permanent_address } : emptyAddress(),
            }));
          }}
        />
        Same as Permanent Address
      </label>
      {!form.same_as_permanent && renderAddressBlock("correspondence", "Correspondence Address")}
    </div>
  );

  const renderCommunication = () => (
    <div className="grid md:grid-cols-2 gap-4">
      <Field label="Mobile Number"><Input value={form.mobile_number} onChange={(e) => update("mobile_number", e.target.value)} /></Field>
      <Field label="Alternate Number"><Input value={form.alternate_number} onChange={(e) => update("alternate_number", e.target.value)} /></Field>
      <Field label="Personal Email"><Input type="email" value={form.personal_email} onChange={(e) => update("personal_email", e.target.value)} /></Field>
      <Field label="Company Email"><Input type="email" value={form.company_email} disabled className="bg-slate-100" /></Field>
    </div>
  );

  const listSection = (itemsKey, emptyItem, fields, title, addLabel) => (
    <div className="space-y-4">
      {form[itemsKey].map((item, idx) => (
        <div key={idx} className="border rounded-lg p-4 relative">
          <div className="grid md:grid-cols-2 gap-3">
            {fields.map((f) => (
              <Field key={f.key} label={f.label}>
                {f.type === "date" ? (
                  <Input
                    type="date"
                    value={item[f.key] || ""}
                    onChange={(e) => {
                      const list = [...form[itemsKey]];
                      list[idx] = { ...list[idx], [f.key]: e.target.value };
                      update(itemsKey, list);
                    }}
                  />
                ) : (
                  <Input
                    value={item[f.key] || ""}
                    onChange={(e) => {
                      const list = [...form[itemsKey]];
                      list[idx] = { ...list[idx], [f.key]: e.target.value };
                      update(itemsKey, list);
                    }}
                  />
                )}
              </Field>
            ))}
          </div>
          {form[itemsKey].length > 1 && (
            <button
              type="button"
              className="mt-2 text-red-600 text-sm"
              onClick={() => update(itemsKey, form[itemsKey].filter((_, i) => i !== idx))}
            >
              Remove
            </button>
          )}
        </div>
      ))}
      <button type="button" className="text-indigo-600 text-sm font-medium" onClick={() => update(itemsKey, [...form[itemsKey], emptyItem()])}>
        + {addLabel}
      </button>
    </div>
  );

  const renderBank = () => (
    <div className="grid md:grid-cols-2 gap-4">
      {Object.keys(form.bank_details).map((k) => (
        <Field key={k} label={k.replaceAll("_", " ")} className={k === "branch_address" ? "md:col-span-2" : ""}>
          {k === "branch_address" ? (
            <TextArea
              value={form.bank_details[k]}
              onChange={(e) => setForm((p) => ({ ...p, bank_details: { ...p.bank_details, [k]: e.target.value } }))}
            />
          ) : (
            <Input
              value={form.bank_details[k]}
              onChange={(e) => setForm((p) => ({ ...p, bank_details: { ...p.bank_details, [k]: e.target.value } }))}
            />
          )}
        </Field>
      ))}
    </div>
  );

  const renderSkills = () => (
    <div className="grid md:grid-cols-2 gap-4">
      {[
        ["certification_name", "Certification Name"],
        ["certification_provider", "Provider"],
        ["certification_issue_date", "Issue Date"],
        ["certification_expiry_date", "Expiry Date"],
        ["technical_skills", "Technical Skills"],
        ["soft_skills", "Soft Skills"],
        ["programming_languages", "Programming Languages"],
        ["frameworks", "Frameworks"],
        ["tools", "Tools"],
      ].map(([key, label]) => (
        <Field key={key} label={label} className={key.includes("skills") || key === "tools" ? "md:col-span-2" : ""}>
          {key.includes("date") ? (
            <Input
              type="date"
              value={form.skills[key]}
              onChange={(e) => setForm((p) => ({ ...p, skills: { ...p.skills, [key]: e.target.value } }))}
            />
          ) : key.includes("skills") || key === "tools" || key === "frameworks" || key === "programming_languages" ? (
            <TextArea
              value={form.skills[key]}
              onChange={(e) => setForm((p) => ({ ...p, skills: { ...p.skills, [key]: e.target.value } }))}
              placeholder="Comma-separated values"
            />
          ) : (
            <Input
              value={form.skills[key]}
              onChange={(e) => setForm((p) => ({ ...p, skills: { ...p.skills, [key]: e.target.value } }))}
            />
          )}
        </Field>
      ))}
    </div>
  );

  const renderLanguages = () => (
      <div className="space-y-4">
        {form.languages.map((lang, idx) => (
          <div key={idx} className="border rounded-lg p-4">
            <Field label="Language">
              <Input
                value={lang.language}
                onChange={(e) => {
                  const list = [...form.languages];
                  list[idx] = { ...list[idx], language: e.target.value };
                  update("languages", list);
                }}
              />
            </Field>
            <div className="flex flex-wrap gap-4 mt-2">
              {["can_speak", "can_read", "can_write", "can_understand"].map((flag) => (
                <label key={flag} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={lang[flag]}
                    onChange={(e) => {
                      const list = [...form.languages];
                      list[idx] = { ...list[idx], [flag]: e.target.checked };
                      update("languages", list);
                    }}
                  />
                  {flag.replace("can_", "").replace(/^./, (c) => c.toUpperCase())}
                </label>
              ))}
            </div>
            {form.languages.length > 1 && (
              <button type="button" className="mt-2 text-red-600 text-sm" onClick={() => update("languages", form.languages.filter((_, i) => i !== idx))}>
                Remove
              </button>
            )}
          </div>
        ))}
        <button type="button" className="text-indigo-600 text-sm font-medium" onClick={() => update("languages", [...form.languages, { language: "", can_speak: false, can_read: false, can_write: false, can_understand: false }])}>
          + Add Language
        </button>
      </div>
    );

  const renderInterests = () => (
    <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-2">
      {INTEREST_OPTIONS.map((interest) => (
        <label key={interest} className="flex items-center gap-2 border rounded-lg p-3 text-sm cursor-pointer hover:bg-slate-50">
          <input
            type="checkbox"
            checked={form.interests.includes(interest)}
            onChange={(e) => {
              if (e.target.checked) update("interests", [...form.interests, interest]);
              else update("interests", form.interests.filter((i) => i !== interest));
            }}
          />
          {interest}
        </label>
      ))}
    </div>
  );

  const renderDocuments = () => (
    <div className="grid md:grid-cols-2 gap-4">
      {DOCUMENT_TYPES.map((d) => (
        <Field key={d.key} label={d.label}>
          <DragDropUpload
            compact
            value={form.pendingFiles?.[d.key] || null}
            onChange={(file) => update("pendingFiles", { ...form.pendingFiles, [d.key]: file })}
          />
        </Field>
      ))}
    </div>
  );

  const stepContent = {
    1: renderEmployment,
    2: renderPersonal,
    3: renderGov,
    4: renderAddress,
    5: renderCommunication,
    6: () =>
      listSection(
        "family_members",
        () => ({ name: "", relationship: "", date_of_birth: "", occupation: "", company: "" }),
        [
          { key: "name", label: "Name" },
          { key: "relationship", label: "Relationship" },
          { key: "date_of_birth", label: "Date of Birth", type: "date" },
          { key: "occupation", label: "Occupation" },
          { key: "company", label: "Company" },
        ],
        "Family",
        "Add Family Member"
      ),
    7: renderBank,
    8: () =>
      listSection(
        "education",
        () => ({ degree: "", institute: "", board_university: "", year_of_passing: "", percentage: "", major_subjects: "" }),
        [
          { key: "degree", label: "Degree" },
          { key: "institute", label: "Institute" },
          { key: "board_university", label: "Board/University" },
          { key: "year_of_passing", label: "Year" },
          { key: "percentage", label: "Percentage" },
          { key: "major_subjects", label: "Major Subjects" },
        ],
        "Education",
        "Add Education"
      ),
    9: () =>
      listSection(
        "experience",
        () => ({
          company_name: "",
          industry: "",
          designation: "",
          employment_type: "",
          start_date: "",
          end_date: "",
          reason_for_leaving: "",
        }),
        [
          { key: "company_name", label: "Company" },
          { key: "industry", label: "Industry" },
          { key: "designation", label: "Designation" },
          { key: "employment_type", label: "Employment Type" },
          { key: "start_date", label: "Start Date", type: "date" },
          { key: "end_date", label: "End Date", type: "date" },
          { key: "reason_for_leaving", label: "Reason for Leaving" },
        ],
        "Experience",
        "Add Experience"
      ),
    10: renderSkills,
    11: renderLanguages,
    12: renderInterests,
    13: renderDocuments,
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex gap-2 overflow-x-auto pb-2">
        {PROFILE_STEPS.map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => setStep(s.id)}
            className={`whitespace-nowrap px-3 py-1.5 rounded-full text-sm border ${
              step === s.id ? "bg-indigo-600 text-white border-indigo-600" : "bg-white text-slate-700"
            }`}
          >
            {s.id}. {s.title}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow p-6 min-h-[320px]">
        <h3 className="text-lg font-semibold mb-4">{PROFILE_STEPS.find((s) => s.id === step)?.title}</h3>
        {stepContent[step]?.()}
      </div>

      <div className="flex justify-between">
        <button type="button" disabled={step <= 1} onClick={() => setStep((s) => s - 1)} className="px-4 py-2 border rounded-lg disabled:opacity-40">
          Previous
        </button>
        <div className="flex gap-2">
          {step < PROFILE_STEPS.length ? (
            <button type="button" onClick={() => setStep((s) => s + 1)} className="px-4 py-2 bg-slate-800 text-white rounded-lg">
              Next
            </button>
          ) : (
            <button type="submit" disabled={submitting} className="px-6 py-2 bg-indigo-600 text-white rounded-lg disabled:opacity-50">
              {submitting ? "Saving..." : isEdit ? "Update Employee" : "Create Employee"}
            </button>
          )}
        </div>
      </div>
    </form>
  );
}
